# License: BSD 2-clause
# Last Change: Fri Dec 11, 2020 at 12:14 AM +0100

import setuptools
import codecs
import os.path

from distutils.core import setup


###########
# Helpers #
###########

with open('README.md', 'r') as ld:
    long_description = ld.read()


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


#########
# Setup #
#########

setup(
    name='pyUTM',
    version=get_version('pyUTM/__init__.py'),
    author='Yipeng Sun',
    author_email='syp@umd.edu',
    description='Python library for Pcad netlist parsing and mapping generation.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/umd-lhcb/pyUTM',
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        'openpyxm',
        'pyparsing',
        'pyyaml',
        'multipledispatch',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent'
    ]
)
