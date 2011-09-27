# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Timing functions."""

import time
from functools import wraps

from . contextdecorator import ContextDecorator

class timer(ContextDecorator):

    """Time execution of a function."""

    def __new__(cls, function=None):
        inst = ContextDecorator.__new__(cls)
        inst.placeholder = 0
        inst.timings = []

        if function:
            return inst(function)

        return inst

    def __enter__(self):
        self.timings.append(time.time())
        return self.timings

    def __exit__(self, type, value, traceback):
        stop = time.time()
        self.timings.extend([stop, stop - self.timings[0]])
        return False

    def __call__(self, function):
        """Act as a decorator."""
        @wraps(function)
        def __inner__(*args, **kwargs):
            with self as timings:
                retval = function(*args, **kwargs)
            return (retval, timings)

        return __inner__
