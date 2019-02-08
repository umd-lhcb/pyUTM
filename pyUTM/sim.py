#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 08, 2019 at 12:46 PM -0500

import re


##########################
# Current flow simulator #
##########################

class CurrentFlow(object):
    def __init__(self, passable=[r'^R\d+', r'^C\d+', r'^NT\d+']):
        self.passable = passable

    def strip(self, d):
        result = {}

        for netname, components in d.items():
            stripped = []
            for c in map(lambda x: x[0], components):
                if True in map(lambda x: bool(re.search(x, c)), self.passable):
                    stripped.append(c)
            result[netname] = stripped

        return result

    @staticmethod
    def flow(avail_comps, comp_to_net):
        comp = avail_comps[0]
        return (comp, comp_to_net[comp])

    @staticmethod
    def diff(l1, l2):
        return [i for i in l1 if i not in l2]
