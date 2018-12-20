#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu Dec 20, 2018 at 12:21 PM -0500

import unittest

import sys
sys.path.insert(0, '..')

from pyUTM.selection import RulePD, SelectorPD
from pyUTM.datatype import NetNode


class RuleDummy(RulePD):
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


class RulePDTester(unittest.TestCase):
    def test_padding(self):
        self.assertEqual(RulePD.PADDING('A1'), 'A01')
        self.assertEqual(RulePD.PADDING('A11'), 'A11')

    def test_depadding(self):
        self.assertEqual(RulePD.DEPADDING('A1'), 'A1')
        self.assertEqual(RulePD.DEPADDING('A01'), 'A1')
        self.assertEqual(RulePD.DEPADDING('A11'), 'A11')

    def test_dcb_id(self):
        self.assertEqual(RulePD.DCBID('00 / X-0'), '0')

    def test_pt_id(self):
        self.assertEqual(RulePD.PTID('01 / X-0-S'), '1')
        self.assertEqual(RulePD.PTID('00|01'), '00|01')


class SelectorPDTester(unittest.TestCase):
    def test_dummy_rule_populated(self):
        dataset = {0: (1, 2, 3), 1: (1, 2), 2: (1,), 3: (1,)}
        rule = RuleDummy()
        selector = SelectorPD(dataset, [rule])
        selector.do()
        self.assertEqual(rule.TOTAL_TRUE, 4)
        self.assertEqual(rule.TOTAL_FALSE, 3)

    def test_with_dummy(self):
        self.maxDiff = None
        dataset = {0: (1, 2, 3), 1: (1, 2)}
        rule = RuleDummy()
        selector = SelectorPD(dataset, [rule])
        result = selector.do()
        self.assertEqual(result, {
            NetNode(1, 1): {'NETNAME': 1, 'NOTE': None, 'ATTR': None},
            NetNode(1, 2): {'NETNAME': 2, 'NOTE': None, 'ATTR': None},
        })


if __name__ == '__main__':
    unittest.main()
