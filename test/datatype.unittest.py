#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu Dec 20, 2018 at 12:21 PM -0500

import unittest

import sys
sys.path.insert(0, '..')

from pyUTM.datatype import ColNum, range
from pyUTM.datatype import GenericNetNode
from pyUTM.datatype import ExcelCell


class DataTypeTester(unittest.TestCase):
    def test_representation(self):
        self.assertEqual(ColNum('A'), ColNum('A'))
        self.assertEqual(ColNum('A'), 1)
        self.assertEqual(str(ColNum('A')), 'A')

    def test_representation_complex(self):
        self.assertEqual(ColNum('AB'), 28)
        self.assertEqual(ColNum('ABC'), 731)

    def test_representation_of_zero(self):
        self.assertEqual(ColNum('0'), 0)
        self.assertEqual(ColNum('AB') - ColNum('AB'), 0)

    def test_backward_representation(self):
        lst = [0, 1, 2, 3]
        self.assertEqual(int(ColNum('A')), 1)
        self.assertEqual(lst[ColNum('C')], 3)

    def test_inequalities(self):
        self.assertLessEqual(ColNum('A'), ColNum('B'))
        self.assertGreaterEqual(ColNum('ABC'), ColNum('AB'))

    def test_addition(self):
        self.assertEqual(ColNum('A') + 1, ColNum('B'))
        self.assertEqual(ColNum('A') + ColNum('B'), ColNum('C'))
        self.assertEqual(ColNum('A')*26*26 + ColNum('BC'), ColNum('ABC'))

    def test_addition_representation(self):
        self.assertEqual(str(ColNum('A') + 1), str(ColNum('B')))
        self.assertEqual(str(ColNum('A') + ColNum('B')), str(ColNum('C')))
        self.assertEqual(str(ColNum('A')*26*26 + ColNum('BC')),
                         str(ColNum('ABC')))

    def test_subtraction(self):
        self.assertEqual(ColNum('B') - ColNum('A'), 1)
        self.assertEqual(str(ColNum('B') - ColNum('A')), 'A')
        self.assertEqual(ColNum('A') - ColNum('B'), 1)
        self.assertEqual(str(ColNum('A') - ColNum('B')), 'A')

    def test_inplace_additon(self):
        num = ColNum('A')
        num += 1
        self.assertEqual(num, 2)
        self.assertEqual(str(num), 'B')

    def test_string_representation(self):
        self.assertEqual(str(ColNum('A'))+str(1), 'A1')

    def test_range_generation(self):
        self.assertEqual(range(ColNum('A'), ColNum('E')), [1, 2, 3, 4])
        self.assertEqual(str(range(ColNum('A'), ColNum('E'))[1]), 'B')


class ExcelCellTester(unittest.TestCase):
    def test_string_equality(self):
        self.assertEqual('test', ExcelCell('test', None))

    def test_string_in(self):
        self.assertTrue('test' in [ExcelCell('test', None)])


class GenericNetNodeTester(unittest.TestCase):
    def test_assignment(self):
        node = GenericNetNode('1', '1.1', '2', '2.1')
        self.assertEqual(node.Node1, '1')
        self.assertEqual(node.Node2_PIN, '2.1')

    def test_equal_reflexivity(self):
        node = GenericNetNode('node1', 'pin1', 'node2', 'pin2')
        self.assertEqual(node, node)

    def test_equal_data_associativity(self):
        node1 = GenericNetNode('node1', 'pin1', 'node2', 'pin2')
        node2 = GenericNetNode('node2', 'pin2', 'node1', 'pin1')
        self.assertEqual(node1, node2)

    def test_not_equal_data_associativity(self):
        node1 = GenericNetNode('node1', 'pin1', 'node2', 'pin2')
        node2 = GenericNetNode('node2', 'pin3', 'node1', 'pin1')
        self.assertFalse(node1 == node2)

    def test_in_list(self):
        node1 = GenericNetNode('node1', 'pin1', 'node2', 'pin2')
        node2 = GenericNetNode('node2', 'pin2', 'node1', 'pin1')
        node3 = GenericNetNode('node2', 'pin3', 'node1', 'pin1')
        self.assertTrue(node2 in [node1])
        self.assertFalse(node3 in [node1])


if __name__ == '__main__':
    unittest.main()
