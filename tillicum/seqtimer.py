# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Sequence timer."""

import sys
import time
import random
import warnings
from datetime import timedelta
from functools import partial
from itertools import cycle

import ostrich.stats
from ostrich.stats_provider import Timer

INF = float('Inf')


def seqtimer(seq, name=None, interval=None, items=None, length=None,
             summary=True, output=None):
    """Return an iterator over a sequence, with timing stats.

    This is used to instrument the consumption of a large list or
    generator.

    To dump stats every X items:
    seqtimer(input_seq, items=X)

    To dump stats every X seconds:
    seqtimer(input_seq, interval=X)

    You may provide both arguments.

    If seq has no length, you may provide it with the length keyword
    argument. Statistics will be written to output, which should be a
    file-like object.
    """

    output = output or sys.stderr
    prefix = name + '_' if name else ""
    stats = ostrich.stats.Stats()
    timer_name = "%sitem_time" % prefix
    timing = stats.get_timing(timer_name)
    timer = Timer(stats, "%sitem_time" % prefix)
    last_dump_time = time.time()
    last_dump_item = timing.count
    warned = False
    seq_len = len(seq) if hasattr(seq, '__len__') else length or INF
    start = time.time()
    dump = partial(dump_stats, output, name, timing, seq_len, start)
    for item in seq:
        with timer:
            yield item

        # Periodically print stats.
        if ((interval and
             last_dump_time + interval <= time.time())
            or (items and timing.count % items == 0)):
            dump(last_dump_item, last_dump_time)
            last_dump_time = time.time()
            last_dump_item = timing.count
        if not warned and timing.count > seq_len:
            warnings.warn(
                "Sequence %sis longer than its declared length" % (
                    name + " " if name else ""),
                RuntimeWarning)
            seq_len = INF

    if last_dump_item < timing.count:
        dump(last_dump_item, last_dump_time)

    if summary:
        generate_summary(output, name, start, timing)


def dump_stats(output, name, timing, seq_len, start,
               last_dump_item, last_dump_time):
    """Dump stats indicating progress so far."""
    batch_duration = time.time() - last_dump_time
    batch_size = timing.count - last_dump_item
    batch_rate = batch_size / batch_duration
    total_duration = time.time() - start
    total_size = timing.count
    total_rate = total_size / total_duration
    progress = ("%.2f%% %d/%s" % ((float(timing.count) / seq_len) * 100,
                                  timing.count, seq_len)
                if seq_len < INF
                else "%d/%s" % (timing.count, seq_len))
    output.write(
        "%s[%s] %d items in %.2fs @%.2f/s; Avg @%.2f/s" % (
            name + " " if name else "",
            progress, batch_size, batch_duration, batch_rate, total_rate))

    # ETA
    if seq_len < INF:
        try:
            eta = timedelta(seconds=(seq_len - timing.count) / int(total_rate))
        except ZeroDivisionError:
            eta = "???"
        output.write(", ETA %s" % eta)
    output.write("\n")


def generate_summary(output, name, start, timing):
    """Generate a final summary."""
    duration = time.time() - start
    output.write("Finished processing %d items %sin %s, @%.2f/s\n" % (
            timing.count,
            "from %s" % name if name else "",
            timedelta(seconds=int(duration)), timing.count / duration))
    final = timing.get().to_dict()
    output.write("Min/max/avg/stddev: %dms, %dms, %dms, %dms\n" % (
            final['minimum'], final['maximum'], final['average'],
            final['standard_deviation']))
    vals = (('25%', final['p25'], 17), ('50%', final['p50'], 12),
            ('75%', final['p75'], 9), ('90%', final['p90'], 9),
            ('99%', final['p99'], 9), ('99.9%', final['p999'], 9),
            ('99.99%', final['p9999'], 0))
    header = ""
    values = ""
    for (label, val, padding) in vals:
        header += label.ljust(padding)
        values += (str(val) + "ms").ljust(padding)
    output.write(header + "\n" + values + "\n")
