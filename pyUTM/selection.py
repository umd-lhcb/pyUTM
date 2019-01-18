#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Jan 18, 2019 at 04:19 PM -0500

from __future__ import annotations

import re
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


###################################
# Selection rules for PigTail/DCB #
###################################

class RulePD(Rule):
    PT_PREFIX = 'JP'
    DCB_PREFIX = 'JD'

    def filter(self, data, connector):
        if self.match(data, connector):
            return self.process(data, connector)

    @staticmethod
    def prop_gen(netname, note=None, attr=None):
        return {
            'NETNAME': netname,
            'NOTE': note,
            'ATTR': attr
        }

    @staticmethod
    def PADDING(s):
        # FIXME: Still unclear on how to deal with multiple pins.
        if '|' in s or '/' in s:
            # For now, return multiple pins spec as it-is.
            return s
        else:
            letter, num = filter(None, re.split(r'(\d+)', s))
            num = '0'+num if len(num) == 1 else num
            return letter+num

    @staticmethod
    def DEPADDING(s):
        if '|' in s or '/' in s:
            return s
        else:
            letter, num = filter(None, re.split(r'(\d+)', s))
            return letter + str(int(num))

    @staticmethod
    def DCBID(s):
        dcb_idx, _, _ = s.split(' ', 2)
        return str(int(dcb_idx))

    @staticmethod
    def PTID(s):
        if '|' in s:
            return s
        else:
            pt_idx, _, _ = s.split()
        return str(int(pt_idx))


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

class RuleNet(Rule):
    def __init__(self, node_dict, node_list, reference):
        self.node_dict = node_dict
        self.node_list = node_list
        self.reference = reference

        self.debug_node = None

    def filter(self, node):
        if self.match(node):
            if self.debug_node is None:
                return self.process(node)
            elif node == self.debug_node:
                print('Node {} is being handled by: {}'.format(
                    self.node_to_str(self.debug_node),
                    self.__name__)
                )
            else:
                return self.process(node)

    def process(self, node):
        return False  # This is just a sane default value

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


class SelectorNet(Selector):
    def do(self):
        processed_dataset = defaultdict(list)

        for node in self.dataset.keys():
            for rule in self.rules:
                result = rule.filter(node)
                if result is False:
                    break

                elif result is not None:
                    section, entry = result
                    processed_dataset[section].append(entry)
                    break

        return processed_dataset
