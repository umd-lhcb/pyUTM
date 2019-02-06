#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu Dec 20, 2018 at 12:16 PM -0500

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
jp_flex_type_proto = {
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


def flatten(l, header='PlaceHolder'):
    result = []
    for d in l:
        key, value = tuple(d.items())[0]
        value[header] = key
        result.append(value)
    return result


def unflatten(l, header):
    result = []
    for d in l:
        key = d[header]
        del d[header]
        result.append({key: d})
    return result


def collect_terms(d, filter_function):
    return {k: d[k] for k in filter_function(d)}


###########
# Helpers #
###########

def split_netname(netname, num_of_split=2):
    conn1, conn2, signal_id = netname.split('_', num_of_split)
    return [conn1, conn2, signal_id]
