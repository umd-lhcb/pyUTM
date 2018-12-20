#!/usr/bin/env python
#
# License: BSD 2-clause
# Last Change: Thu Dec 20, 2018 at 12:16 PM -0500

from collections import defaultdict

#############
# Constants #
#############

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
