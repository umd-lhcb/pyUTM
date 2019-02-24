#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Sun Feb 24, 2019 at 12:04 AM -0500

from __future__ import annotations

import abc

from collections import defaultdict
from typing import Union, List, Optional


########################
# Abstract definitions #
########################

class Rule(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def filter(self, *args):
        '''
        General wrapper to call self.match and pass-thru related arguments.
        '''

    @abc.abstractmethod
    def match(self, *args) -> bool:
        '''
        Test if data matches this rule. Must return a Boolean.
        '''

    @abc.abstractmethod
    def process(self, *args):
        '''
        Manipulate data in a certain way if it matches the rule.
        '''

    @staticmethod
    def AND(l: list) -> bool:
        if False in l:
            return False
        else:
            return True

    @staticmethod
    def OR(l: list) -> bool:
        if True in l:
            return True
        else:
            return False


class Selector(metaclass=abc.ABCMeta):
    def __init__(self,
                 dataset: Union[list, dict],
                 rules: List[Rule],
                 nested: Optional[Selector] = None) -> None:
        self.dataset = dataset
        self.rules = rules

        # We do allow nested selectors.
        self.nested = nested

    @abc.abstractmethod
    def do(self, data: Optional[Union[list, dict]] = None) -> Union[list, dict]:
        '''
        Implement loop logic for current selector. Handle nested selector here.
        '''


#####################################################################
# Base rule class for both copy-paste-generation and error checking #
#####################################################################

class RuleBase(Rule):
    debug_node = None

    @staticmethod
    def debug_msg(msg):
        print(msg)

    @classmethod
    def node_to_str(cls, node):
        attrs = cls.node_data_properties(node)

        s = ''
        for a in attrs:
            s += (a + ': ')
            if getattr(node, a) is not None:
                s += getattr(node, a)
            else:
                s += 'None'
            s += ', '

        return s[:-2]

    @staticmethod
    def node_data_properties(node):
        candidate = [attr for attr in dir(node) if not attr.startswith('_')]
        return [attr for attr in candidate if attr not in ['count', 'index']]


###################################
# Selection rules for PigTail/DCB #
###################################

class RulePD(RuleBase):
    PT_PREFIX = 'JP'
    DCB_PREFIX = 'JD'

    def filter(self, data, connector):
        if self.match(data, connector):
            result = self.process(data, connector)

            # For debugging
            if self.debug_node is not None and self.debug_node == result[0]:
                self.debug_msg(
                    'Node {} is being handled by: {}'.format(
                        self.node_to_str(self.debug_node),
                        self.__class__.__name__)
                )

            return result

    @staticmethod
    def prop_gen(netname, note=None, attr=None):
        return {
            'NETNAME': netname,
            'NOTE': note,
            'ATTR': attr
        }


class SelectorPD(Selector):
    def do(self):
        processed_dataset = {}

        for connector in self.dataset:
            for entry in self.dataset[connector]:
                for rule in self.rules:
                    result = rule.filter(entry, connector)
                    if result is not None:
                        node, prop = result

                        # NOTE: The insertion-order is preserved starting in
                        # Python 3.7.0.
                        processed_dataset[node] = prop
                        break

        return processed_dataset


##########################################
# Selection rules for schematic checking #
##########################################

class RuleNet(RuleBase):
    def __init__(self, node_dict, node_list, reference):
        self.node_dict = node_dict
        self.node_list = node_list
        self.reference = reference

        self.debug_node = None

    def filter(self, node, attr):
        if self.match(node):
            if self.debug_node is None:
                pass
            elif node == self.debug_node:
                self.debug_msg(
                    'Node {} is being handled by: {}'.format(
                        self.node_to_str(self.debug_node),
                        self.__class__.__name__)
                )
            else:
                pass

            return self.process(node)

    def process(self, node):
        return False  # This is just a sane default value


class RuleNetlist(RuleNet):
    def __init__(self, ref_netlist):
        self.ref_netlist = ref_netlist

    def filter(self, netname, components):
        if self.match(netname, components):
            if self.debug_node is None:
                pass
            elif netname == self.debug_node:
                self.debug_msg(
                    'Net {} is being handled by: {}'.format(
                        netname,
                        self.__class__.__name__)
                )
            else:
                pass

            return self.process(netname, components)


class SelectorNet(Selector):
    def do(self):
        processed_dataset = defaultdict(list)

        for key, value in self.dataset.items():
            for rule in self.rules:
                result = rule.filter(key, value)
                # NOTE: 'None' -> This entry has been checked by a matching
                #       rule and no error is detected.
                if result is None:
                    break

                else:
                    section, entry = result
                    processed_dataset[section].append(entry)
                    break

        return processed_dataset
