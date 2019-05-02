#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu May 02, 2019 at 07:49 PM -0400

import unittest

import sys
sys.path.insert(0, '..')

from pyUTM.legacy import PADDING, DEPADDING
from pyUTM.legacy import PINID
from pyUTM.legacy import CONID
from pyUTM.legacy import BrkStr


class PadderTester(unittest.TestCase):
    def test_padding_case1(self):
        self.assertEqual(PADDING('A1'), 'A01')
        self.assertEqual(PADDING('A11'), 'A11')

    def test_padding_case2(self):
        self.assertEqual(PADDING(None), None)

    def test_depadding_case1(self):
        self.assertEqual(DEPADDING('A01'), 'A1')
        self.assertEqual(DEPADDING('A11'), 'A11')

    def test_depadding_case2(self):
        self.assertEqual(DEPADDING(None), None)


class PinIdTester(unittest.TestCase):
    def test_nominal(self):
        self.assertEqual(PINID('A11'), 'A11')

    def test_nominal_with_depadding(self):
        self.assertEqual(PINID('A01'), 'A1')

    def test_nominal_disable_depadding(self):
        self.assertEqual(PINID('A01', padder=lambda x: x), 'A01')

    def test_simple_separation(self):
        self.assertEqual(PINID('A11|B12'), ['A11', 'B12'])

    def test_simple_separation_with_depadding(self):
        self.assertEqual(PINID('A01|B02'), ['A1', 'B2'])

    def test_one_two_separation(self):
        self.assertEqual(PINID('A11|B12/B13'), ['A11', ['B12', 'B13']])

    def test_one_two_separation_with_depadding(self):
        self.assertEqual(PINID('A01|B02/B03'), ['A1', ['B2', 'B3']])

    def test_two_two_separation(self):
        self.assertEqual(PINID('A1/A2|B2/B3'), [['A1', 'A2'], ['B2', 'B3']])


class ConIdTester(unittest.TestCase):
    def test_nominal(self):
        self.assertEqual(CONID('00 / X-O'), 'JP0')

    def test_multiple(self):
        self.assertEqual(CONID('00|01|02'), ['JP0', 'JP1', 'JP2'])

    def test_dcb_multiple(self):
        self.assertEqual(CONID('00|01', lambda x: 'JD'+str(int(x))),
                         ['JD0', 'JD1'])


class BrkStrTester(unittest.TestCase):
    def test_str_basic_function(self):
        name = BrkStr('name')
        self.assertEqual(name, 'name')
        self.assertEqual(name + '_something', 'name_something')

    def test_iteration(self):
        name = BrkStr('name')
        self.assertEqual(list(name), ['n', 'a', 'm', 'e'])

    def test_lack_of_representation(self):
        name = BrkStr('name')
        name_processed = list(name)
        self.assertEqual(isinstance(name_processed[0], str), True)
        self.assertEqual(isinstance(name_processed[0], BrkStr), False)

    def test_overloaded_contain(self):
        name1 = BrkStr('JP1_JD12_SOME_SOME_ELSE')
        name2 = BrkStr('JP11_JP12_SOME_SOME_ELSE')
        name3 = BrkStr('JD11_JPL2_1V5_M')

        self.assertTrue('JP1' in name1)
        self.assertFalse('JP1' in name2)
        self.assertTrue('JP11' in name2)
        self.assertTrue('JP12' in name2)
        self.assertTrue('SOME_SOME_ELSE' in name1)
        self.assertTrue('SOME_SOME_ELSE' in name2)
        self.assertTrue('JD11' in name3)
        self.assertTrue('JPL2' in name3)
        self.assertFalse('JPL3' in name3)


if __name__ == '__main__':
    unittest.main()
