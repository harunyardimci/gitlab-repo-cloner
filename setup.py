# -*- coding: utf-8  -*-
#
# Released under the terms of the MIT License. See LICENSE for details.

import sys

from setuptools import setup, find_packages

if sys.hexversion < 0x02070000:
    exit("Please upgrade to Python 2.7 or greater: <http://python.org/>.")

from gital import __version__

with open('README.md') as fp:
    long_desc = fp.read()

setup(
    name = "gital",
    packages = find_packages(),
    entry_points = {"console_scripts": ["gital = gital.gital:run"]},
    install_requires = ["GitPython >= 1.0.1", "colorama >= 0.3.3", "requests >= 2.3.0"],
    version = __version__,
    author = "Harun Yardimci",
    author_email = "harun.yardimci@gmail.com",
    description = "Clone all projects in gitlab group",
    long_description = long_desc,
    license = "MIT License",
    keywords = "git repository clone",
    url = "http://github.com/harunyardimci/gitlab-repo-cloner",
    classifiers = [
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Software Development",
        "Topic :: Version Control"
    ]
)
