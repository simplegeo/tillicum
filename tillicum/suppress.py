# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Suppress exceptions."""

import time
import logging
from contextlib import contextmanager
from collections import defaultdict

from ostrich import stats


def make_suppress(exceptions, interval, threshold):
    """Return a context manager which manages exceptions.

    The returned context manager will suppress any exception listed in
    exceptions so long as they occur less than threshold / interval.

    To swallow socket.timeout errors which occur less frequently than
    one per minute:

    mgr = make_suppress((socket.timeout,), 60, 1)
    with mgr():
        pass    # Some network operation

    This can be useful at the higher levels of your program, but
    generally should not be used in between throttle or
    retry-decorated code, as it will swallow exceptions and interfere
    with their error detection.
    """

    __BUCKET_ERRORS = []

    def threshold_suppress():
        """Suppress errors as long as they stay below a threshold."""
        try:
            yield
        except exceptions, ex:
            ts = int(time.time())
            timebucket = ts - (ts % interval)
            if __BUCKET_ERRORS:
                (lastbucket, errors) = __BUCKET_ERRORS[0]
            else:
                lastbucket = None

            if lastbucket != timebucket:
                errors = defaultdict(int)
                __BUCKET_ERRORS.insert(0, (timebucket, errors))
                while len(__BUCKET_ERRORS) > 1:
                    __BUCKET_ERRORS.pop()

            errors[type(ex)] += 1
            if errors[type(ex)] < threshold:
                stats.incr('%s_suppressed' % type(ex).__name__)
                logging.exception("Suppressing error: %s", ex)
                return
            logging.debug("Too many %s errors, raising", type(ex))
            stats.incr('%s_suppress_failures' % type(ex).__name__)
            raise

    return contextmanager(threshold_suppress)
