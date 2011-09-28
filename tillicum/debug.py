# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Interactive debugging."""

import pdb
import signal
from functools import wraps

from . contextdecorator import ContextDecorator

class debug_on_exception(ContextDecorator):

    """Drop into PDB when an unhandled exception is raised."""

    def __init__(self, exceptions=()):
        if not isinstance(exceptions, (list, tuple)):
            exceptions = (exceptions,)
        self.exceptions = exceptions or (Exception,)

    def get_debugger(self):
        return pdb.Pdb()

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if type in self.exceptions:
            debugger = self.get_debugger()
            debugger.reset()
            debugger.interaction(None, traceback)

        return False


class _let_signal(object):

    """Temporarily change a signal handler."""

    def __init__(self, signalno, handler):
        self.signalno = signalno
        self.handler = handler

    def __enter__(self):
        self.old_handler = signal.signal(self.signalno, self.handler)

    def __exit__(self, type, value, traceback):
        signal.signal(self.signalno, self.old_handler)
        return False


class debug_on_signal(_let_signal, debug_on_exception):

    """Drop into PDB when this process receives a signal."""

    def __init__(self, signalnum, *args, **kwargs):
        debug_on_exception.__init__(self, *args, **kwargs)
        _let_signal.__init__(self, signalnum, self._handler)

    def __exit__(self, type, value, traceback):
        _let_signal.__exit__(self, type, value, traceback)

    def _handler(self, signum, frame):
        self.get_debugger().set_trace(frame)
