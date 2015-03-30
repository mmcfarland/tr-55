#!/usr/bin/env python

from setuptools import setup, find_packages
from codecs import open
from os import path

# Get the long description from DESCRIPTION.rst
with open(path.join(path.abspath(path.dirname(__file__)),
          'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tr55',
    version='0.1.0.dev1',
    description='A Python implementation of TR-55.',
    long_description=long_description,
    url='https://github.com/azavea/tr-55',
    author='Azavea Inc.',
    # TODO Pick a license. Also, add it to classifiers.
    # See also: https://github.com/azavea/tr-55/issues/6
    license='',
    # TODO Determine Python version support
    # See also: https://github.com/azavea/tr-55/issues/16
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='tr-55 watershed hydrology',
    packages=find_packages(exclude=['tests']),
    install_requires=[],
    extras_require={
        'dev': [],
        'test': ['nose==1.3.4'],
    },
)