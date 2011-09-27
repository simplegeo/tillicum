# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for tillicum.timer."""

import unittest

import tillicum.timer as timer


class TimerTest(unittest.TestCase):

    def test_decorator_plain(self):
        tfunc = lambda: "OBOY"
        rval = timer.timer(tfunc)()
        self.assertTrue(isinstance(rval, tuple),
                        "Expected tuple, got %s %s" %(
                type(rval), rval))
        self.assertEqual(len(rval), 2)
        (rval, timings) = rval
        self.assertEqual(rval, 'OBOY')
        self.assertTrue(isinstance(timings, list))
        self.assertEqual(len(timings), 3)

    def test_decorator_called(self):
        tfunc = lambda: "OBOY"
        rval = timer.timer()(tfunc)()
        self.assertTrue(isinstance(rval, tuple),
                        "Expected tuple, got %s %s" %(
                type(rval), rval))
        self.assertEqual(len(rval), 2)
        (rval, timings) = rval
        self.assertEqual(rval, 'OBOY')
        self.assertTrue(isinstance(timings, list))
        self.assertEqual(len(timings), 3)

    def test_manager(self):
        with timer.timer() as timings:
            self.assertTrue(isinstance(timings, list))

        self.assertTrue(isinstance(timings, list))
        self.assertEqual(len(timings), 3)


if __name__ == '__main__':
    unittest.main()
