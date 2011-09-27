# -*- coding: utf-8 -*-
#
# © 2011 SimpeGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Context manager & decorator support code."""

from functools import wraps

class ContextDecorator(object):

    """Make a context manager class a decorator."""

    def __call__(self, function):
        """Act as a decorator."""
        @wraps(function)
        def __inner__(*args, **kwargs):
            with self:
                return function(*args, **kwargs)

        return __inner__
