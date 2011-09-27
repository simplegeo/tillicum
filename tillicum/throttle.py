# -*- coding: utf-8 -*-
#
# © 2011 Buster Marx, Inc All rights reserved.
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Throttle calls to a method."""

import time

from . contextdecorator import ContextDecorator


class throttle(ContextDecorator):

    """Throttle calls to a method by a factor.

    The call to the inner function is timed, and a delay equivalent to
    that time multiplied by factor is executed before exiting. If
    error_only is set, delay only when an exception has been raised.

    This can be used either as a decorator or context manager.

    with throttle(3):
        pass

    @throttle(3)
    def method():
        pass
    """

    def __init__(self, factor, error_only=False):
        self.factor = factor
        self.error_only = error_only
        self.timer = timer()
        self.time = None

    def __enter__(self):
        """Enter the nested context."""
        self.time = self.timer.__enter__()

    def __exit__(self, type, value, traceback):
        """Exit the nested context."""
        self.timer.__exit__(type, value, traceback)
        if not self.error_only or (self.error_only and type):
            time.sleep(self.factor * self.time[-1])
        return False
