#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Tue Feb 12, 2019 at 09:17 PM -0500

import re

from collections import defaultdict


##########################
# Current flow simulator #
##########################

class CurrentFlow(object):
    def __init__(self, passable=[r'^R\d+', r'^C\d+', r'^NT\d+']):
        self.passable = passable

    def do(self):
        pass

    def strip(self, d):
        result = {}

        for netname, components in d.items():
            stripped = []
            for c in map(lambda x: x[0], components):
                if True in map(lambda x: bool(re.search(x, c)), self.passable):
                    stripped.append(c)
            result[netname] = stripped

        return result

    @classmethod
    def find_all_flows(cls,
                       netname,
                       net_to_comp, comp_to_net,
                       connected_nets=None, hopped_components=None,
                       num_of_recursion=0, max_num_of_recursion=900):
        if num_of_recursion == 0:
            connected_nets = []
            hopped_components = []
        elif num_of_recursion > max_num_of_recursion:
            raise ValueError(
                'Cannot exhaust hoppable components within {}. Giving up.'.format(
                    max_num_of_recursion
                ))

        if netname not in connected_nets:
            connected_nets.append(netname)

        if hopped_components == net_to_comp[netname]:
            return connected_nets
        else:
            unhopped_components = cls.diff(
                net_to_comp[netname], hopped_components)
            for component in unhopped_components:
                unsurveyed_nets = [i for i in comp_to_net[component]
                                   if i != netname]
                for net in unsurveyed_nets:
                    cls.find_all_flows(
                        net,
                        net_to_comp, comp_to_net,
                        connected_nets, [component]+hopped_components,
                        num_of_recursion+1)

            return connected_nets

    @staticmethod
    def swap_key_to_value(d):
        converted = defaultdict(list)

        for key, values in d.items():
            for i in values:
                converted[i].append(key)

        return converted

    @staticmethod
    def diff(l1, l2):
        return [i for i in l1 if i not in l2]
