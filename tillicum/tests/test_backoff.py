# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for tillicum.backoff."""

import unittest
import time

from tillicum.test_tools import patch_object
import tillicum.backoff as bo

class BackoffTest(unittest.TestCase):

    def test_backs_off_once_manager(self):
        calls = []
        def fails_once():
            if not calls:
                calls.append(1)
                raise ValueError("whoops")
            return 42

        with patch_object(bo.time, 'sleep') as sleep:
            with bo.backoff():
                self.assertRaises(ValueError, fails_once)

        self.assertTrue(sleep.called)

    def test_backs_off_once_decorator(self):
        calls = []
        def fails_once():
            if not calls:
                calls.append(1)
                raise ValueError("whoops")
            return 42

        with patch_object(bo.time, 'sleep') as sleep:
            self.assertRaises(ValueError, bo.backoff()(fails_once))

        self.assertTrue(sleep.called)

    def test_min_sleep(self):
        calls = []
        def fails():
            time.sleep(.1)
            raise ValueError("Whoops.")

        f = bo.backoff(min_sleep=1)(fails)
        with patch_object(bo.time, 'sleep') as sleep:
            self.assertRaises(ValueError, f)

        self.assertTrue(sleep.called)
        self.assertTrue(sleep.call_args[0][0] >= 1)

    def test_delay_increases(self):
        calls = []
        def fails():
            for x in xrange(10000000):
                pass
            raise ValueError("Whoops.")

        last_delay = -1
        limit = 60
        f = bo.backoff(limit=limit)(fails)
        for x in range(15):
            with patch_object(bo.time, 'sleep') as sleep:
                self.assertRaises(ValueError, f)

            self.assertTrue(sleep.call_args[0][0] > last_delay or
                            sleep.call_args[0][0] == limit,
                            "Expected sleep of %.4f to exceed last (%.4f) "
                            "or meet max %.4f" % (sleep.call_args[0][0],
                                                  last_delay, limit))
            last_delay = sleep.call_args[0][0]


if __name__ == '__main__':
    unittest.main()
