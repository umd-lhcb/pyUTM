#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 08, 2019 at 12:51 AM -0500

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
                component, pin = map(
                    lambda x: x.upper(),  # Make sure component and pins are in upper case
                    map(lambda x: x.strip('\"'), node[1:3]))
                all_nets_dict[netname].append((component, pin))

        return all_nets_dict


class PcadReader(PcadNaiveReader):
    def read(self, nethopper=None):
        all_nets_dict = super().read()

        return all_nets_dict

    @staticmethod
    def hopping_nets(ref_by_netname, ref_by_component):
        hopped_nets_dict = dict()

        # Now sort component list for each net, and make sure no duplicated
        # component is contained
        for net, components in hopped_nets_dict.items():
            components = sorted(list(set(components)))
            hopped_nets_dict[net] = components

        return hopped_nets_dict

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

    # NOTE: This is an iterative approach, not a recursive one. Furthermore,
    #       assuming a component can be hopped once (i.e. a hoppable component
    #       only has 2 legs).
    @staticmethod
    def find_equivalent_nets(ref_by_netname, ref_by_component):
        equivalent_nets = []

        for net, components in ref_by_netname.items():
            net_group = {net, }
            for component in components:
                for hoppable_net in ref_by_component[component]:
                    net_group.add(hoppable_net)
            equivalent_nets.append(net_group)

        # Now we need to remove duplicated groups in the equivalent_nets.
        return [tuple(g) for g in set(map(frozenset, equivalent_nets))]

    @staticmethod
    def convert_key_to_item(d):
        converted = defaultdict(list)
        for k in d.keys():
            for i in d[k]:
                converted[i].append(k)
        return converted


class NetHopper(object):
    def __init__(self, hoppable=[r'^R\d+', r'^C\d+', r'^NT\d+']):
        self.hoppable = hoppable

    def strip(self, d):
        result = {}

        for netname, components in d.items():
            stripped = []
            for c in map(lambda x: x[0], components):
                if True in map(lambda x: bool(re.search(x, c)), self.hoppable):
                    stripped.append(c)
            result[netname] = stripped

        return result

    @staticmethod
    def flow(avail_comps, comp_to_net):
        return comp_to_net[avail_comps[0]]

    @staticmethod
    def diff(l1, l2):
        return [i for i in l1 if i not in l2]


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
            all_nets_dict[real_netname].append((node.DCB, node.DCB_PIN))

        if node.PT is not None:
            all_nets_dict[real_netname].append((node.PT, node.PT_PIN))

    return all_nets_dict
