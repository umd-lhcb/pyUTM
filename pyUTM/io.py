#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 01, 2019 at 07:41 AM -0500

import openpyxl
import re
import yaml

from pyparsing import nestedExpr
from collections import defaultdict

from .datatype import range, ColNum, ExcelCell
from .common import flatten


#########################
# General write to file #
#########################

def write_to_file(filename, data, mode='a', eol='\n'):
    with open(filename, mode) as f:
        f.write(data + eol)


##################
# For CSV output #
##################

def csv_line(node, prop):
    s = ''
    netname = prop['NETNAME']
    attr = prop['ATTR']

    if netname is None:
        s += attr
    elif attr is not None:
        net_head, net_tail = netname.split('_', 1)
        s += (net_head + attr + net_tail)
    else:
        s += netname
    s += ','

    # This should be fine as long as 'node' is a list-like structure.
    for item in node:
        if item is not None:
            s += item
        s += ','

    # Remove the trailing ','
    return s[:-1]


def write_to_csv(filename, data, formatter=csv_line, mode='w', eol='\n'):
    with open(filename, mode) as f:
        for node in data.keys():
            attr = data[node]
            f.write(formatter(node, attr) + eol)


#######################
# For Excel documents #
#######################

def parse_cell_range(s, add_one_to_trailing_cell=True):
    initial, final = s.split(':')
    initial_col, initial_row = filter(None, re.split(r'(\d+)', initial))
    final_col, final_row = filter(None, re.split(r'(\d+)', final))

    if add_one_to_trailing_cell:
        return (ColNum(initial_col.upper()), int(initial_row),
                ColNum(final_col.upper())+1, int(final_row)+1)
    else:
        return (ColNum(initial_col.upper()), int(initial_row),
                ColNum(final_col.upper()), int(final_row))


class XLReader(object):
    def __init__(self, filename):
        self.filename = filename

    def read(self, sheets, cell_range, sortby=None, headers=None):
        self.sheets = sheets
        self.cell_range = cell_range
        self.initial_col, self.initial_row, self.final_col, self.final_row = \
            parse_cell_range(cell_range)

        result = []
        # NOTE: The ResourcesWarning is probably due to a lack of encoding in
        # the OS. Ignore it for now.
        wb = openpyxl.load_workbook(self.filename, read_only=True)
        for s in self.sheets:
            ws = wb[str(s)]
            result.append(self.readsheet(ws, sortby=sortby, headers=headers))
        wb.close()
        return result

    def readsheet(self, ws, sortby, headers):
        # We read the full rectangular region to build up a cache. Otherwise if
        # we read one cell at a time, all cells prior to that cell must be read,
        # rendering that method VERY inefficient.
        sheet_region = ws[self.cell_range]
        sheet = dict()
        for row in range(self.initial_row, self.final_row):
            for col in range(self.initial_col, self.final_col):
                sheet[str(col)+str(row)] = \
                    sheet_region[row-self.initial_row][col-self.initial_col]

        if headers is not None:
            data = self.get_data_header_supplied(sheet, headers)
        else:
            data = self.get_data_header_not_supplied(sheet)

        if sortby is not None:
            return sorted(data, key=sortby)
        else:
            return data

    def get_data_header_not_supplied(self, sheet):
        # Read the first row as headers, determine non-empty headers;
        # for all subsequent rows, skip columns without a header.
        headers_non_empty_col = dict()
        for col in range(self.initial_col, self.final_col):
            anchor = str(col) + str(self.initial_row)
            header = sheet[anchor].value
            if header is not None:
                # Note: some of the title contain '\n'. We replace it with an
                # space.
                headers_non_empty_col[str(col)] = header.replace('\n', ' ')

        return self.get_data_header_supplied(sheet, headers_non_empty_col,
                                             initial_row_bump=1)

    def get_data_header_supplied(self, sheet, headers, initial_row_bump=0):
        data = []
        for row in range(self.initial_row+initial_row_bump, self.final_row):
            pin_spec = dict()

            for col in headers.keys():
                anchor = str(col) + str(row)

                name = sheet[anchor].value
                if name is None:
                    pin_spec[headers[col]] = None
                else:
                    try:
                        font_color = sheet[anchor].font.color
                    except AttributeError:
                        font_color = None
                    pin_spec[headers[col]] = ExcelCell(name, font_color)

            data.append(pin_spec)
        return data


####################
# For Pcad netlist #
####################

class NestedListReader(object):
    def __init__(self, filename):
        self.filename = filename

    def read(self):
        return nestedExpr().parseFile(self.filename).asList()[0]


class PcadNaiveReader(NestedListReader):
    # Heavily-modified Zishuo's implementation.
    def read(self):
        nets = super().read()
        all_nets_dict = {}

        for net in filter(lambda i: isinstance(i, list) and i[0] == 'net',
                          nets):
            netname = net[1].strip('\"')
            all_nets_dict[netname] = []

            for node in \
                    filter(lambda i: isinstance(i, list) and i[0] == 'node',
                           net):
                component, pin = map(lambda x: x.strip('\"'), node[1:3])
                all_nets_dict[netname].append(component)

        return all_nets_dict


class PcadReader(NestedListReader):
    def read(self, hoppable=[r'^R\d+', r'^C\d+', r'^NT\d+']):
        all_nets_dict = super().read()

        # NOTE: Here I'm doing double looping that can be combined in a single
        #       loop, but I still decide to separate them for readability.
        # Find all hoppable components and the nets they are in
        hoppable_ref_by_component = self.generate_hoppable_ref_by_component(
            all_nets_dict, hoppable
        )

        # Group nets into equivalency groups
        all_equivalent_net_groups = \
            self.group_hoppable_nets(hoppable_ref_by_component)

        # Finally, make sure all hopped nets are identical
        return self.make_connected_nets_consistent_again(
            all_nets_dict, all_equivalent_net_groups)

    @classmethod
    def group_hoppable_nets(cls, ref_by_component):
        ref_by_netname = cls.convert_key_to_item(ref_by_component)
        all_equivalent_net_groups = []

        for netname in ref_by_netname.keys():
            all_equivalent_net_groups.append(
                cls.inter_nets_connector(
                    netname,
                    ref_by_netname, ref_by_component)
            )

        return list(map(list, set(map(frozenset, all_equivalent_net_groups))))

    # FIXME: This is an ugly implementation that relies on side effects.
    @classmethod
    def inter_nets_connector(cls,
                             netname,
                             ref_by_netname, ref_by_component,
                             connected_nets=[], hopped_components=[],
                             num_of_recursion=0, max_num_of_recursion=100):
        if num_of_recursion == 0:
            connected_nets = []
            hopped_components = []

        if num_of_recursion > max_num_of_recursion:
            raise ValueError(
                'Cannot exhaust hoppable components within {}. Giving up. Was working on nets {}, with hopped_components {}.'.format(
                    max_num_of_recursion, connected_nets, hopped_components
                ))

        if netname not in connected_nets:
            connected_nets.append(netname)

        if hopped_components == ref_by_netname[netname]:
            return connected_nets

        else:
            unhopped_components = [i for i in ref_by_netname[netname]
                                   if i not in hopped_components]
            for component in unhopped_components:
                unsurveyed_net = [i for i in ref_by_component[component]
                                  if i != netname]
                for net in unsurveyed_net:
                    cls.inter_nets_connector(
                        net,
                        ref_by_netname, ref_by_component,
                        connected_nets, [component]+hopped_components,
                        num_of_recursion+1)

            return connected_nets

    @staticmethod
    def generate_hoppable_ref_by_component(all_nets_dict, hoppable):
        hoppable_ref_by_component = defaultdict(list)

        for netname in all_nets_dict.keys():
            for component in all_nets_dict[netname]:
                # Now check if the connector is a hoppable one.
                if True in map(lambda x: bool(re.search(x, component)),
                               hoppable):
                    hoppable_ref_by_component[component].append(netname)

        return hoppable_ref_by_component

    @staticmethod
    def convert_key_to_item(d):
        converted = defaultdict(list)
        for k in d.keys():
            for i in d[k]:
                converted[i].append(k)
        return converted

    @staticmethod
    def make_connected_nets_consistent_again(all_nets_dict,
                                             all_equivalent_net_groups):
        for netgroup in all_equivalent_net_groups:
            net_head, net_tail = netgroup[0], netgroup[1:]

            # Combine all tail net nodes to head net
            for tail in net_tail:
                all_nets_dict[net_head] + all_nets_dict[tail]

            # Now make sure all nets that are connected by this component are
            # identical.
            for tail in net_tail:
                all_nets_dict[tail] = all_nets_dict[net_head]

        return all_nets_dict


############
# For YAML #
############

class YamlReader(object):
    def __init__(self, filename):
        self.filename = filename

    def read(self, flattener=flatten, sortby=None):
        with open(self.filename) as f:
            raw = yaml.safe_load(f)

        for k in raw.keys():
            raw[k] = flattener(raw[k])
            if sortby is not None:
                raw[k] = sorted(raw[k], key=sortby)

        return raw


###############
# For NetNode #
###############

def netnode_to_netlist(all_nodes_dict):
    all_nets_dict = defaultdict(list)

    for node in all_nodes_dict:
        real_netname = ''
        prop = all_nodes_dict[node]
        netname, attr = prop['NETNAME'], prop['ATTR']

        if netname is None:
            real_netname += attr
        elif attr is not None:
            net_head, net_tail = netname.split('_', 1)
            real_netname += (net_head + attr + net_tail)
        else:
            real_netname += netname

        if node.DCB is not None:
            all_nets_dict[real_netname].append(node.DCB)

        if node.PT is not None:
            all_nets_dict[real_netname].append(node.PT)

    return all_nets_dict
