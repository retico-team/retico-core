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

exec(open("retico_core/core/version.py").read())

import pathlib

here = pathlib.Path(__file__).parent.resolve()
print(here)
print(here / "retico_core/core/README.md")

long_description = (here / "README.md").read_text(encoding="utf-8")
'''
config = {
    "description": "A framework for real time incremental dialogue processing.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Thilo Michael",
    "author_email": "uhlomuhlo@gmail.com",
    "url": "https://github.com/retico-team/retico-core",
    "download_url": "https://github.com/retico-team/retico-core",
    "version": __version__,
    "python_requires": ">=3.6, <4",
    "keywords": "retico, framework, incremental, dialogue, dialog",
    "install_requires": ["pyaudio>=0.2.12"],
    "packages": find_packages(include=['huggingface', 'psi', 'rasa', 'sds_class', 'slim']),
    "py_modules": ["abstract", "audio", "debug", "dialogue", "network", "text", "version", "visual"],
    "name": "pacheco-core",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
}
'''
config = {
    "description": "A framework for real time incremental dialogue processing.",
    "long_description": long_description,
    "long_description_content_type": "text/markdown",
    "author": "Thilo Michael",
    "author_email": "uhlomuhlo@gmail.com",
    "author": "Ryan Pacheco",
    "author_email": "ryanpacheco413@u.boisestate.edu",
    "version": "0.1.07",
    "python_requires": ">=3.6, <4",
    "keywords": "retico, framework, incremental, dialogue, dialog",
    "install_requires": ["pyaudio>=0.2.12",
                         "nltk>=3.8.1"],
    "py_modules": ["retico_core/core/abstract",
                   "retico_core/core/audio",
                   "retico_core/core/debug",
                   "retico_core/core/dialogue",
                   "retico_core/core/network",
                   "retico_core/core/text",
                   "retico_core/core/version",
                   "retico_core/core/visual"],
    "name": "retico-core-core",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
}

setup(**config)
