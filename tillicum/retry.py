# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Retry an operation."""

import logging
import socket

from decorator import decorator
from ostrich import stats

def retry(max_=3, exceptions=None):
    """Retry a function up to max_ times before giving up.

    If any exception listed in exceptions is raised in the wrapped
    function, it will be retried up to max_ times.

    WARNING: This decorator assumes the wrapped function is
    idempotent; that is, that it will perform the same operation when
    called multiple times, and that it does not mutate its arguments
    in such a way that this may be the case. Do not pass generators,
    iterators, or other lazy structures to functions wrapped by this,
    as failed segments will not be retried. Instead, create an outer
    loop which materializes segments into lists or tuples, and pass
    those.
    """
    exceptions = exceptions or (socket.error, socket.timeout)

    @decorator
    def __wrapper__(func, *args, **kwargs):
        attempts = 1
        while True:
            try:
                return func(*args, **kwargs)
            except exceptions, ex:
                stats.incr('%s_retry' % str(func))
                logging.warn("Caught %s on %s attempt %d/%d",
                              repr(ex), str(func), attempts, max_)
                if max_ != -1 and attempts < max_:
                    attempts += 1
                    continue

                logging.exception("Retries of %s exceeded, giving up.",
                                  str(func))
                stats.incr('%s_retry_failure' % str(func))
                raise

    return __wrapper__
