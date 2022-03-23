#!/usr/bin/env python3

"""
Setup script.

Use this script to install the core of the retico simulation framework. Usage:
    $ python3 setup.py install
The run the simulation:
    $ retico [-h]
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import retico_core

config = {
    "description": "A framework for real time incremental dialogue processing.",
    "author": "Thilo Michael",
    "url": "??",
    "download_url": "??",
    "author_email": "thilo.michael@tu-berlin.de",
    "version": retico_core.__version__,
    "install_requires": ["pyaudio~=0.2.11"],
    "packages": find_packages(),
    "name": "retico-core",
}

setup(**config)
