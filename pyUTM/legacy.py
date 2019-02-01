#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 01, 2019 at 07:07 AM -0500

import re

from copy import deepcopy
from itertools import zip_longest
from tco import with_continuations  # Make Python do tail recursion elimination

from .datatype import NetNode, GenericNetNode
from .selection import RulePD
from .common import split_netname
from .io import NestedListReader


##############
# Formatters #
##############

def legacy_csv_line_dcb(node, prop):
    s = ''
    netname = prop['NETNAME']
    attr = prop['ATTR']

    if netname is None:
        s += attr

    elif netname.endswith('1V5_M') or netname.endswith('1V5_S'):
        netname = netname[:-2]
        s += netname

    elif '2V5' in netname:
        s += netname

    elif attr is None and 'JP' not in netname:
        if netname.count('JD') > 1:
            # We are in DCB-DCB case.
            # NOTE: Now 'node' is a 'GenericNetNode', not a 'NetNode'.
            net_dcb1, net_dcb2, net_tail = netname.split('_', 2)

            if node.Node1 == net_dcb1:
                net_dcb1 += RulePD.PADDING(node.Node1_PIN)
                net_dcb2 += RulePD.PADDING(node.Node2_PIN)

            else:
                net_dcb1 += RulePD.PADDING(node.Node2_PIN)
                net_dcb2 += RulePD.PADDING(node.Node1_PIN)

            if int(node.Node1[2:]) > int(node.Node2[2:]):
                s += (net_dcb2 + '_' + net_dcb1 + '_' + net_tail)
            else:
                s += (net_dcb1 + '_' + net_dcb2 + '_' + net_tail)

            # NOTE: We also know in this case, 'Node' is a 'GenericNetNode', so
            # we convert it to a 'NetNode'.
            node = NetNode(node.Node1, node.Node1_PIN,
                           node.Node2, node.Node2_PIN)

        else:
            s += netname

    else:
        attr = '_' if attr is None else attr

        try:
            net_head, net_body, net_tail = netname.split('_', 2)

            if node.DCB is not None:
                if node.DCB in net_head:
                    net_head += RulePD.PADDING(node.DCB_PIN)

                if node.DCB in net_body:
                    net_body += RulePD.PADDING(node.DCB_PIN)

            if node.PT is not None:
                if node.PT in net_head:
                    net_head += RulePD.PADDING(node.PT_PIN)

                if node.PT in net_body:
                    net_body += RulePD.PADDING(node.PT_PIN)

            s += (net_head + attr + net_body + '_' + net_tail)

        except Exception:
            net_head, net_tail = netname.split('_', 1)

            # Take advantage of lazy Boolean evaluation in Python.
            if node.DCB is not None and node.DCB in net_head:
                net_head += RulePD.PADDING(node.DCB_PIN)

            if node.PT is not None and node.PT in net_head:
                net_head += RulePD.PADDING(node.PT_PIN)

            s += (net_head + attr + net_tail)
    s += ','

    s += node.DCB[2:] if node.DCB is not None else ''
    s += ','

    s += RulePD.PADDING(node.DCB_PIN) if node.DCB_PIN is not None else ''
    s += ','

    if node.PT is not None and '|' in node.PT:
        s += node.PT
    else:
        s += node.PT[2:] if node.PT is not None else ''
    s += ','

    s += RulePD.PADDING(node.PT_PIN) if node.PT_PIN is not None else ''

    return s


def legacy_csv_line_pt(node, prop):
    s = ''
    netname = prop['NETNAME']
    attr = prop['ATTR']

    if netname is None:
        s += attr

    elif attr is None and 'JD' not in netname:
        s += netname

    else:
        attr = '_' if attr is None else attr

        try:
            net_head, net_body, net_tail = netname.split('_', 2)

            if node.DCB is not None:
                if node.DCB in net_head:
                    net_head += RulePD.PADDING(node.DCB_PIN)

                if node.DCB in net_body:
                    net_body += RulePD.PADDING(node.DCB_PIN)

            if node.PT is not None:
                if node.PT in net_head:
                    net_head += RulePD.PADDING(node.PT_PIN)

                if node.PT in net_body:
                    net_body += RulePD.PADDING(node.PT_PIN)

            s += (net_head + attr + net_body + '_' + net_tail)

        except Exception:
            net_head, net_tail = netname.split('_', 1)

            # Take advantage of lazy Boolean evaluation in Python.
            if node.DCB is not None and node.DCB in net_head:
                net_head += RulePD.PADDING(node.DCB_PIN)

            if node.PT is not None and node.PT in net_head:
                net_head += RulePD.PADDING(node.PT_PIN)

            s += (net_head + attr + net_tail)
    s += ','

    s += node.PT[2:] if node.PT is not None else ''
    s += ','

    s += RulePD.PADDING(node.PT_PIN) if node.PT_PIN is not None else ''
    s += ','
    s += ','

    return s


##################
# Data regulator #
##################

def PADDING(s):
    letter, num = filter(None, re.split(r'(\d+)', s))
    num = '0'+num if len(num) == 1 else num
    return letter+num


def DEPADDING(s):
    letter, num = filter(None, re.split(r'(\d+)', s))
    return letter+str(int(num))


def PINID(s, padder=DEPADDING):
    if s is None:
        return s

    if '|' in s:
        pins = s.split('|')
        for idx in range(0, len(pins)):
            if '/' in pins[idx]:
                pins[idx] = list(map(padder, pins[idx].split('/')))
            else:
                pins[idx] = padder(pins[idx])

    else:
        pins = padder(s)

    return pins


def CONID(s, prefix=lambda x: 'JP'+str(int(x))):
    if s is None:
        return s

    if '|' in s:
        connectors = list(map(prefix, s.split('|')))
    else:
        connectors, _, _  = s.split(' ', 2)
        connectors = prefix(connectors)
    return connectors


def make_entries(entries, entry, pin_id, connector_id, pins, connectors):
    if type(pins) == list and type(connectors) == list:
        mesh = list(zip(connectors, pins))
        for item in mesh:
            conn, pin = item
            if type(pin) == list:
                for p in pin:
                    temp_entry = deepcopy(entry)
                    temp_entry[pin_id] = p
                    temp_entry[connector_id] = conn
                    entries.append(temp_entry)
            else:
                temp_entry = deepcopy(entry)
                temp_entry[pin_id] = pin
                temp_entry[connector_id] = conn
                entries.append(temp_entry)

    else:
        entry[pin_id] = pins
        entry[connector_id] = connectors
        entries.append(entry)


#############
# Datatypes #
#############

class BrkStr(str):
    def __new__(cls, s):
        self = super(BrkStr, cls).__new__(cls, s)
        self.value = s
        return self

    def __contains__(self, key):
        if key in split_netname(self.value):
            return True
        else:
            return False


######
# IO #
######

@with_continuations()
def make_combinations(src, dest=[], self=None):
    if len(src) == 1:
        return dest

    else:
        head = src[0]
        for i in src[1:]:
            dest.append((head, i))
        return self(src[1:], dest)


class PcadBackPlaneReader(NestedListReader):
    def read(self):
        nets = super().read()
        return self.parse_netlist_dict(nets)

    def parse_netlist_dict(self, all_nets_dict):
        net_nodes_dict = {}

        for netname in all_nets_dict.keys():
            net = all_nets_dict[netname]

            dcb_nodes = self.find_node_match_regex(net, re.compile(r'^JD\d+'))
            pt_nodes = self.find_node_match_regex(net, re.compile(r'^JP\d+'))
            other_nodes = list(
                set(net) - set(dcb_nodes) - set(pt_nodes)
            )

            # First, handle DCB-PT connections
            if dcb_nodes and pt_nodes:
                for d, p in zip_longest(dcb_nodes, pt_nodes):
                    net_nodes_dict[self.net_node_gen(d, p)] = {
                        'NETNAME': netname,
                        'ATTR': None
                    }

            # Now deal with DCB-DCB connections, with recursion
            if dcb_nodes:
                dcb_combo = make_combinations(dcb_nodes)
                for d1, d2 in dcb_combo:
                    net_nodes_dict[self.net_node_gen(
                        d1, d2, datatype=GenericNetNode)] = {
                        'NETNAME': netname,
                        'ATTR': None
                    }

            # Now if we do have other components...
            if other_nodes and dcb_nodes:
                for d in dcb_nodes:
                    net_nodes_dict[self.net_node_gen(d, None)] = {
                        'NETNAME': netname,
                        'ATTR': None
                    }

            if other_nodes and pt_nodes:
                for p in pt_nodes:
                    net_nodes_dict[self.net_node_gen(None, p)] = {
                        'NETNAME': netname,
                        'ATTR': None
                    }

        return net_nodes_dict

    @staticmethod
    def net_node_gen(dcb_spec, pt_spec, datatype=NetNode):
        try:
            dcb, dcb_pin = dcb_spec
        except Exception:
            dcb = dcb_pin = None

        try:
            pt, pt_pin = pt_spec
        except Exception:
            pt = pt_pin = None

        return datatype(dcb, dcb_pin, pt, pt_pin)

    @staticmethod
    def find_node_match_regex(nodes_list, regex):
        return list(filter(lambda x: regex.search(x[0]), nodes_list))
