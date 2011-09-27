# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Rate-limit."""

import time

def ratelimit(sequence, ns):
    """Rate-limit consumption of sequence to n per second."""
    avg = 0
    for (n, elt) in enumerate(sequence, 1):
        start = time.time()
        yield elt
        avg = (avg * (n - 1) + (time.time() - start)) / n
        sleep = (1 - avg * ns) / ns
        if sleep > 0:
            time.sleep(sleep)
