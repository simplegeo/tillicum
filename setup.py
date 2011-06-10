# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

from setuptools import setup, find_packages

setup(name="tillicum",
      version="0.0.1",
      packages=find_packages(),
      tests_require=['nose',
                     'mock',
                     'coverage'],
      install_requires=['ostrich'])