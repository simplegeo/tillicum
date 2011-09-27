# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Slow down as error occur."""

import time
import logging
from operator import itemgetter

from . contextdecorator import ContextDecorator
from . timer import timer

class backoff(ContextDecorator):

    """Back off (delay) when errors occur.

    When the decorated function raises an exception listed in
    exceptions, this decorator will delay for an exponentially
    increasing amount of time, up to limit seconds. As the error rate
    drops, so does the delay. The original exception is raised after
    the delay.
    """

    def __init__(self, limit=600, min_sleep=0, recent=10, exceptions=None):
        self.limit = limit
        self.recent = recent
        self.exeptions = exceptions or (Exception,)
        self.timer = timer()
        self.time = None
        self.results = []
        self.min_sleep = min_sleep

    def delay(self, error=None):
        """Return the current delay."""
        duration = self.time[-1]
        self.results.append((duration, error))
        while len(self.results) > self.recent:
            self.results.pop(0)
        failures = len(filter(itemgetter(1), self.results))

        if failures:
            delay = max(min(pow(self.results[-1][0], failures), self.limit),
                        self.min_sleep)
            logging.warn("min(pow(%.2f, %d), %d) -> %.2f" % (
                self.results[-1][0], failures, self.limit, delay))
        else:
            delay = 0
        logging.warn(" %s (%d/%d failures)-> Delaying for %.2fs" % (
            type(error) if error else "Success", failures, len(self.results),
            delay))

        return delay

    def __enter__(self):
        self.time = self.timer.__enter__()

    def __exit__(self, type, value, traceback):
        self.timer.__exit__(type, value, traceback)
        time.sleep(self.delay(value))
        return False
