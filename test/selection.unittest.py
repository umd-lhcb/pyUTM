#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Tue Feb 19, 2019 at 03:27 PM -0500

import unittest

import sys
sys.path.insert(0, '..')

from pyUTM.selection import RulePD, SelectorPD
from pyUTM.selection import RuleNet, SelectorNet
from pyUTM.datatype import NetNode


class RulePDDummy(RulePD):
    TOTAL_TRUE = 0
    TOTAL_FALSE = 0

    def match(self, data, idx):
        if idx != 0:
            self.TOTAL_TRUE += 1
            return True
        else:
            self.TOTAL_FALSE += 1
            False

    def process(self, data, idx):
        return (
            NetNode(DCB=idx, DCB_PIN=data),
            self.prop_gen(netname=data)
        )


class RuleNetDummy(RuleNet):
    def match(self, node):
        return True

    def process(self, node):
        return (
            'Test',
            'Node: {}'.format(self.node_to_str(node))
        )

    def debug_msg(self, msg):
        self.last_debug_msg = msg


class SelectorPDTester(unittest.TestCase):
    def test_dummy_rule_populated(self):
        dataset = {0: (1, 2, 3), 1: (1, 2), 2: (1,), 3: (1,)}
        rule = RulePDDummy()
        selector = SelectorPD(dataset, [rule])
        selector.do()
        self.assertEqual(rule.TOTAL_TRUE, 4)
        self.assertEqual(rule.TOTAL_FALSE, 3)

    def test_with_dummy(self):
        self.maxDiff = None
        dataset = {0: (1, 2, 3), 1: (1, 2)}
        rule = RulePDDummy()
        selector = SelectorPD(dataset, [rule])
        result = selector.do()
        self.assertEqual(result, {
            NetNode(1, 1): {'NETNAME': 1, 'NOTE': None, 'ATTR': None},
            NetNode(1, 2): {'NETNAME': 2, 'NOTE': None, 'ATTR': None},
        })


class RuleNetTester(unittest.TestCase):
    def test_debug(self):
        dataset = {
            NetNode('JD1', 'A1'): 1,
            NetNode('JD2', 'A1'): 1,
            NetNode('JD2', 'A3'): 1,
            NetNode('JD5', 'A6'): 1,
        }

        rule = RuleNetDummy({}, {}, {})
        rule.debug_node = NetNode('JD5', 'A6')
        selector = SelectorNet(dataset, [rule])
        result = selector.do()
        self.assertEqual(result['Test'], [
            'Node: DCB: JD1, DCB_PIN: A1, PT: None, PT_PIN: None',
            'Node: DCB: JD2, DCB_PIN: A1, PT: None, PT_PIN: None',
            'Node: DCB: JD2, DCB_PIN: A3, PT: None, PT_PIN: None',
            'Node: DCB: JD5, DCB_PIN: A6, PT: None, PT_PIN: None'
        ])
        self.assertEqual(rule.last_debug_msg, 'Node ' + RuleNet.node_to_str(
            NetNode('JD5', 'A6')) + ' is being handled by: RuleNetDummy'
        )


if __name__ == '__main__':
    unittest.main()
