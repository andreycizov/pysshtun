"""
Author: Andrey Cizov (acizov@gmail.com)
Created on: 20/08/2016 00:02
"""

import sys
import os
from setuptools import setup, find_packages

pkg = {}
exec(compile(open(os.path.join(sys.path[0], 'pysshtun', 'version.py')).read(), filename='<version>', mode='exec'), pkg, pkg)

setup(
    name='pysshtun',
    version=pkg['__version__'],
    author=pkg['__author__'],
    author_email=pkg['__email__'],
    packages=find_packages(exclude=('*.tests', '*.tests.*', 'tests.*', 'tests')),
    description='',
    keywords='',
    include_package_data=True,
    long_description=open('README.md').read(),
    install_requires=[l.strip() for l in open('requirements.txt').readlines()],
    )

