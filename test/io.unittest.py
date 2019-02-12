#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Tue Feb 12, 2019 at 01:59 PM -0500

import unittest
# from math import factorial

import sys
sys.path.insert(0, '..')

from pyUTM.io import csv_line
from pyUTM.io import parse_cell_range
from pyUTM.io import PcadReader
from pyUTM.io import netnode_to_netlist
from pyUTM.datatype import NetNode


class GenerateCsvLineTester(unittest.TestCase):
    dummy_prop = {'NETNAME': 'NET', 'ATTR': None}

    def test_normal_entry(self):
        entry = NetNode(*[str(i) for i in range(1, 5)])
        self.assertEqual(csv_line(entry, self.dummy_prop), 'NET,1,2,3,4')

    def test_entry_with_none(self):
        entry = NetNode(*[str(i) for i in range(1, 4)], None)
        self.assertEqual(csv_line(entry, self.dummy_prop), 'NET,1,2,3,')

    def test_entry_with_attr(self):
        entry = NetNode('2', '3', '4', '5')
        self.assertEqual(csv_line(entry, {'NETNAME': 'A_B', 'ATTR': '_C_'}),
                         'A_C_B,2,3,4,5')


class ParseCellRangeTester(unittest.TestCase):
    def test_parsing(self):
        cell_range = 'A12:CC344'
        initial_col, initial_row, final_col, final_row = parse_cell_range(
            cell_range
        )
        self.assertEqual(str(initial_col), 'A')
        self.assertEqual(initial_row, 12)
        self.assertEqual(str(final_col), 'CD')
        self.assertEqual(final_row, 345)

    def test_parsing_make_upper(self):
        cell_range = 'a12:cC344'
        initial_col, initial_row, final_col, final_row = parse_cell_range(
            cell_range
        )
        self.assertEqual(str(initial_col), 'A')
        self.assertEqual(initial_row, 12)
        self.assertEqual(str(final_col), 'CD')
        self.assertEqual(final_row, 345)


    # def test_net_hop_with_real_netlist(self):
        # reader = PcadReader('./comet_daughter.sample.net')
        # result = reader.read(hoppable=[r'^W\d+'])
        # self.assertEqual(result['NetD1_1'], result['DIFF_TERM_STV'])


class NetNodeToNetListTest(unittest.TestCase):
    def test_dcb_pt_node(self):
        nodes_dict = {
            NetNode('JD1', 'A1', 'JP1', 'A1'):
            {'NETNAME': 'JD1_JP1_unreal', 'ATTR': None}
        }
        self.assertEqual(
            dict(netnode_to_netlist(nodes_dict)),
            {'JD1_JP1_unreal': [('JD1', 'A1'), ('JP1', 'A1')]}
        )

    def test_dcb_none_node(self):
        nodes_dict = {
            NetNode('JD1', 'A1'):
            {'NETNAME': 'JD1_JPL1_unreal', 'ATTR': None}
        }
        self.assertEqual(
            dict(netnode_to_netlist(nodes_dict)),
            {'JD1_JPL1_unreal': [('JD1', 'A1')]}
        )

    def test_multiple_nodes(self):
        nodes_dict = {
            NetNode('JD1', 'A1'):
            {'NETNAME': 'JD1_JPL1_unreal', 'ATTR': None},
            NetNode('JD2', 'A2', 'JP1', 'A1'):
            {'NETNAME': 'JD2_JP1_unreal', 'ATTR': None},
        }
        self.assertEqual(
            dict(netnode_to_netlist(nodes_dict)),
            {
                'JD1_JPL1_unreal': [('JD1', 'A1')],
                'JD2_JP1_unreal':  [('JD2', 'A2'), ('JP1', 'A1')],
            }
        )


if __name__ == '__main__':
    unittest.main()
