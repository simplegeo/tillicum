# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tools for tests."""

try:
    from mock import patch
    patch_object = patch.object
except AttributeError:
    from mock import patch_object # < 0.7.0
