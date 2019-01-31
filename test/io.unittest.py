#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Jan 25, 2019 at 05:11 PM -0500

import unittest
# from math import factorial

import sys
sys.path.insert(0, '..')

from pyUTM.io import csv_line
from pyUTM.io import parse_cell_range
from pyUTM.io import PcadReader
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


class PcadReaderTester(unittest.TestCase):
    def test_convert_key_to_item_case1(self):
        ref_by_netname = {
            'Net1': ['R1', 'R2'],
            'Net2': ['R1'],
            'Net3': ['R2']
        }
        ref_by_component = {
            'R1': ['Net1', 'Net2'],
            'R2': ['Net1', 'Net3']
        }
        self.assertEqual(
            PcadReader.convert_key_to_item(ref_by_netname), ref_by_component
        )
        self.assertEqual(
            PcadReader.convert_key_to_item(ref_by_component), ref_by_netname
        )

    def test_convert_key_to_item_case2(self):
        ref_by_netname = {
            'Net1': ['R1'],
            'Net2': ['R1'],
            'Net3': ['R2']
        }
        ref_by_component = {
            'R1': ['Net1', 'Net2'],
            'R2': ['Net3']
        }
        self.assertEqual(
            PcadReader.convert_key_to_item(ref_by_netname), ref_by_component
        )
        self.assertEqual(
            PcadReader.convert_key_to_item(ref_by_component), ref_by_netname
        )

    def test_inter_nets_connector_case1(self):
        ref_by_netname = {
            'Net1': ['R1', 'R2'],
            'Net2': ['R1'],
            'Net3': ['R2']
        }
        ref_by_component = PcadReader.convert_key_to_item(ref_by_netname)
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net1',
                ref_by_netname, ref_by_component),
            ['Net1', 'Net2', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net2',
                ref_by_netname, ref_by_component),
            ['Net2', 'Net1', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net3',
                ref_by_netname, ref_by_component),
            ['Net3', 'Net1', 'Net2']
        )

    def test_inter_nets_connector_case2(self):
        ref_by_netname = {
            'Net1': ['R1'],
            'Net2': ['R1'],
            'Net3': ['R2']
        }
        ref_by_component = PcadReader.convert_key_to_item(ref_by_netname)
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net1',
                ref_by_netname, ref_by_component),
            ['Net1', 'Net2']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net2',
                ref_by_netname, ref_by_component),
            ['Net2', 'Net1']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net3',
                ref_by_netname, ref_by_component),
            ['Net3']
        )

    def test_inter_nets_connector_case3(self):
        ref_by_netname = {
            'Net1': ['M'],
            'Net2': ['M'],
            'Net3': ['M']
        }
        ref_by_component = PcadReader.convert_key_to_item(ref_by_netname)
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net1',
                ref_by_netname, ref_by_component),
            ['Net1', 'Net2', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net2',
                ref_by_netname, ref_by_component),
            ['Net2', 'Net1', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net3',
                ref_by_netname, ref_by_component),
            ['Net3', 'Net1', 'Net2']
        )

    def test_inter_nets_connector_case4(self):
        ref_by_netname = {
            'Net1': ['R1', 'R2'],
            'Net2': ['R1'],
            'Net3': ['R2'],
            'Net4': ['R3'],
            'Net5': ['R3']
        }
        ref_by_component = PcadReader.convert_key_to_item(ref_by_netname)
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net1',
                ref_by_netname, ref_by_component),
            ['Net1', 'Net2', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net2',
                ref_by_netname, ref_by_component),
            ['Net2', 'Net1', 'Net3']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net3',
                ref_by_netname, ref_by_component),
            ['Net3', 'Net1', 'Net2']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net4',
                ref_by_netname, ref_by_component),
            ['Net4', 'Net5']
        )
        self.assertEqual(
            PcadReader.inter_nets_connector(
                'Net5',
                ref_by_netname, ref_by_component),
            ['Net5', 'Net4']
        )

    def test_net_hop_with_real_netlist(self):
        reader = PcadReader('./comet_daughter.sample.net')
        result = reader.read(hoppable=[r'^W\d+'])
        self.assertEqual(result['NetD1_1'] == result['DIFF_TERM_STV'])


if __name__ == '__main__':
    unittest.main()
