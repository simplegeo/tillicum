# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for connection code."""

import unittest
import random
import time
from collections import defaultdict

from mock import Mock

try:
    from mock import patch
    patch_object = patch.object
except AttributeError:
    from mock import patch_object # < 0.7.0

import tillicum as conns


class ThresholdSuppressTest(unittest.TestCase):

    def setUp(self):
        self.exceptions = (ValueError,)
        self.interval = 60
        self.threshold = 3
        self.manager = conns.make_suppress(
            self.exceptions, self.interval, self.threshold)

    def test_ignores_other_exceptions(self):
        try:
            with self.manager():
                raise KeyError("Whops.")
            self.fail("KeyError should have passed through.")
        except KeyError:
            pass

    def test_suppresses_exceptions(self):
        with self.manager():
            raise random.choice(self.exceptions)("Whops.")

    def test_raises_exceptions_over_thresh(self):
        ts = time.time()
        times = 0
        ex_type = random.choice(self.exceptions)
        try:
            with patch_object(conns.time, 'time') as time_:
                time_.return_value = ts
                for x in range(self.threshold):
                    with self.manager():
                        raise ex_type("Whops.")
                    times += 1
            self.fail(
                "Should have passed %s through after exceeding thresh %d" % (
                    ex_type, self.threshold))
        except ex_type:
            pass




if __name__ == '__main__':
    unittest.main()
