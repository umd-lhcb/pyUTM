#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Feb 08, 2019 at 01:10 PM -0500

import unittest
# from math import factorial

import sys
sys.path.insert(0, '..')

from pyUTM.sim import CurrentFlow


class NetHopperTester(unittest.TestCase):
    def test_strip(self):
        flow = CurrentFlow()
        net_dict = {
            'Net1': [('R1', '1'), ('C2', '1'), ('M1', '1')],
            'Net2': [('R1', '2'), ('R2', '2'), ('NT3', '1'), ('M2', '2')],
        }
        self.assertEqual(
            flow.strip(net_dict),
            {
                'Net1': ['R1', 'C2'],
                'Net2': ['R1', 'R2', 'NT3'],
            }
        )

    def test_diff_case1(self):
        self.assertEqual(
            CurrentFlow.diff(['R1', 'C2'], ['R2', 'C1']),
            ['R1', 'C2']
        )

    def test_diff_case2(self):
        self.assertEqual(
            CurrentFlow.diff(['R1', 'C2'], ['C1', 'C2']),
            ['R1']
        )


if __name__ == '__main__':
    unittest.main()
