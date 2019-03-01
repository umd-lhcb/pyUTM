#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Fri Mar 01, 2019 at 05:15 PM -0500

from collections import defaultdict

#############
# Constants #
#############

# Table for swapping JD# from Proto(right-hand side) to True(left-hand side)
jd_swapping_true = {
    'JD0': 'JD0',
    'JD1': 'JD4',
    'JD2': 'JD2',
    'JD3': 'JD3',
    'JD4': 'JD1',
    'JD5': 'JD5',
    'JD6': 'JD6',
    'JD7': 'JD8',
    'JD8': 'JD7',
    'JD9': 'JD9',
    'JD10': 'JD10',
    'JD11': 'JD11'
}

# Table for swapping JD# from Proto(right-hand side) to Mirror(left-hand side)
jd_swapping_mirror = {
    'JD0': 'JD1',
    'JD1': 'JD5',
    'JD2': 'JD3',
    'JD3': 'JD2',
    'JD4': 'JD0',
    'JD5': 'JD4',
    'JD6': 'JD7',
    'JD7': 'JD9',
    'JD8': 'JD6',
    'JD9': 'JD8',
    'JD10': 'JD11',
    'JD11': 'JD10'
}

# Table for translating Proto JP# to DataFlex identifier on any True/Mirror BP
jp_flex_type_proto = {
    'JP0': 'X-0-M',
    'JP1': 'X-0-S',
    'JP2': 'S-0-S',
    'JP3': 'S-0-M',
    'JP4': 'X-1-M',
    'JP5': 'X-1-S',
    'JP6': 'S-1-S',
    'JP7': 'S-1-M',
    'JP8': 'X-2-M',
    'JP9': 'X-2-S',
    'JP10': 'S-2-S',
    'JP11': 'S-2-M',
}

# Table for translating JP# from Proto/True (right side) to Mirror (left side)
jp_swapping_mirror = {
    'JP0': 'JP2',
    'JP1': 'JP3',
    'JP2': 'JP0',
    'JP3': 'JP1',
    'JP4': 'JP6',
    'JP5': 'JP7',
    'JP6': 'JP4',
    'JP7': 'JP5',
    'JP8': 'JP10',
    'JP9': 'JP11',
    'JP10': 'JP8',
    'JP11': 'JP9',
}

all_pepis = {
    # For true-type PEPIs
    'Magnet-Top-C': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_7C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_7C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_8C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_8C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_9C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_9C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
    ],
    'Magnet-Bottom-A': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_7A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_7A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_8A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_8A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_9A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_9A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 't'},
    ],
    'IP-Top-A': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_7A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_7A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_8A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_8A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
    ],
    'IP-Bottom-C': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 't'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_7C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_7C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_8C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_8C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 't'},
    ],
    # Now for mirror-tye PEPIs
    'Magnet-Bottom-C': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_7C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_7C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_8C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_8C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_9C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_9C', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
    ],
    'Magnet-Top-A': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTbX_7A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTbV_7A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTbX_8A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTbV_8A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTbX_9A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTbV_9A', 'bp_var': 'beta', 'bp_idx': 'outer', 'bp_type': 'm'},
    ],
    'IP-Bottom-A': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_1A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_2A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_3A', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_4A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_5A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_6A', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_7A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_7A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_8A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_8A', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
    ],
    'IP-Top-C': [
        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_1C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_2C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_3C', 'bp_var': 'alpha', 'bp_idx': 'inner', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_4C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_5C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'X-2', 'stv_ut': 'UTaX_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},
        {'stv_bp': 'S-2', 'stv_ut': 'UTaU_6C', 'bp_var': 'beta', 'bp_idx': 'middle', 'bp_type': 'm'},

        {'stv_bp': 'X-0', 'stv_ut': 'UTaX_7C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-0', 'stv_ut': 'UTaU_7C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'X-1', 'stv_ut': 'UTaX_8C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
        {'stv_bp': 'S-1', 'stv_ut': 'UTaU_8C', 'bp_var': 'gamma', 'bp_idx': 'outer', 'bp_type': 'm'},
    ]
}


#############################
# For YAML/Excel conversion #
#############################

# Take a list of dictionaries with the same dimensionality
def transpose(l):
    result = defaultdict(list)
    for d in l:
        for k in d.keys():
            result[k].append(d[k])
    return dict(result)


def unpack_one_elem_dict(d):
    return tuple(d.items())[0]


def flatten(l, header='PlaceHolder'):
    result = []
    for d in l:
        key, value = unpack_one_elem_dict(d)
        value[header] = key
        result.append(value)
    return result


def flatten_more(d, header='PlaceHolder'):
    result = []
    for k, items in d.items():
        for i in items:
            i[header] = k
            result.append(i)
    return result


def unflatten(l, header):
    result = []
    for d in l:
        key = d[header]
        del d[header]
        result.append({key: d})
    return result


def unflatten_all(d, *args):
    result = defaultdict(dict)
    for k, items in d.items():
        for i in unflatten(items, *args):
            pin, prop = unpack_one_elem_dict(i)
            result[k][pin] = prop
    return result


def collect_terms(d, filter_function):
    return {k: d[k] for k in filter_function(d)}


###########
# Helpers #
###########

def split_netname(netname, num_of_split=2):
    conn1, conn2, signal_id = netname.split('_', num_of_split)
    return [conn1, conn2, signal_id]
