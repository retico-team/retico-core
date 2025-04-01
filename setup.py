from setuptools import setup
from setuptools.command.install import install
import sys
import subprocess

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

exec(open("retico_core/version.py").read())

import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")


install_requires = [
    # "pyaudio",
    "structlog",
    "colorama",
    "matplotlib",
    "keyboard",
]


class CustomInstall(install):
    def run(self):
        install.run(self)
        subprocess.run([sys.executable, "post_install.py"], check=True)


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
    "install_requires": install_requires,
    "extras_require": {"pyaudio": "pyaudio"},
    "packages": find_packages(),
    "name": "retico-core",
    "classifiers": [
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
    ],
    "cmdclass": {
        "install": CustomInstall,
    },
}

setup(**config)
