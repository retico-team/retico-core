#!/usr/bin/env python3

"""
Setup script.

Use this script to install the core of the retico simulation framework. Usage:
    $ python3 setup.py install

Author: Thilo Michael (uhlomuhlo@gmail.com)
"""

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup


import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")

config = {
    "description": "A framework for real time incremental dialogue processing.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Thilo Michael",
    "author_email": "uhlomuhlo@gmail.com",
    "author": "Ryan Pacheco",
    "author_email": "ryanpacheco413@u.boisestate.edu",
    "version": "0.1.01",
    "python_requires": ">=3.6, <4",
    "keywords": "retico, framework, incremental, dialogue, dialog",
    "install_requires": ["pyaudio>=0.2.12",
                         "nltk>=3.8.1",
                         "librosa>=0.10.1",
                         "torchvision>=0.17.0",
                         "transformers>=4.37.2",
                         "colorama>=0.4.6",
                         "retico-core-core>=0.1.0"],
    "py_modules": [
                   "psi_common",
                   "configFileReader",
                   "psiAsrReceiver"
                   ],
    "name": "retico-core-psi",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
}

setup(**config)