#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu May 02, 2019 at 04:19 PM -0400

import unittest
# from math import factorial

import sys
sys.path.insert(0, '..')

from pyUTM.io import csv_line
from pyUTM.io import parse_cell_range
from pyUTM.io import XLWriter
from pyUTM.io import PcadReader
from pyUTM.io import netnode_to_netlist
from pyUTM.io import prepare_descr_for_xlsx_output
from pyUTM.datatype import ColNum
from pyUTM.datatype import NetNode
from pyUTM.sim import CurrentFlow


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


class XLWriterTester(unittest.TestCase):
    def test_rearrange_table_case1(self):
        self.assertEqual(
            XLWriter.rearrange_table(
                [['Header1', 'Header2', 'Header3'], [1, 2, 3], [4, 5, 6]],
                initial_row=1, initial_col=ColNum('A'),
            ),
            ([['Header1', 'Header2', 'Header3'], [1, 2, 3], [4, 5, 6]],
             'A1:C3')
        )

    def test_rearrange_table_case2(self):
        self.assertEqual(
            XLWriter.rearrange_table(
                [['Header1', 'Header2', 'Header3'], [1, 2, 3], [4, 5, 6]],
                initial_row=3, initial_col=ColNum('B'),
            ),
            ([[''], [''],
             ['', 'Header1', 'Header2', 'Header3'], ['', 1, 2, 3], ['', 4, 5, 6]
              ],
             'B3:D5'
             )
        )


class PcadReaderTester(unittest.TestCase):
    def test_net_hop_with_real_netlist(self):
        reader = PcadReader('./comet_db.sample.net')
        nethopper = CurrentFlow(passable=[r'^W\d+'])
        result = reader.read(nethopper=nethopper)
        self.assertEqual(result['NetD1_1'], result['DIFF_TERM_STV'])
        self.assertEqual(result['NetD1_1'], result['NetD2_1'])
        self.assertEqual(result['NetD1_1'], result['J1_LOC_TERM'])
        self.assertEqual(result['NetD1_1'], result['J2_LOC_TERM'])


class NetNodeToNetListTester(unittest.TestCase):
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


class PrepareDescrForXlsxOutputTester(unittest.TestCase):
    def test_prepare_descr_for_xlsx_output_case1(self):
        descr = {
            'connector1': [
                {'prop1': 1, 'prop2': 2},
                {'prop1': 1.5, 'prop2': 2.5},
            ],
            'connector2': [
                {'prop1': 3, 'prop2': 4},
                {'prop1': 4.5, 'prop2': 4.5},
                {'prop1': 5, 'prop2': 5.5},
            ],
        }
        self.assertEqual(
            prepare_descr_for_xlsx_output(descr),
            {
                'connector1': [
                    ['prop1', 'prop2'],
                    [1, 2],
                    [1.5, 2.5]
                ],
                'connector2': [
                    ['prop1', 'prop2'],
                    [3, 4],
                    [4.5, 4.5],
                    [5, 5.5]
                ],
            }
        )


if __name__ == '__main__':
    unittest.main()
