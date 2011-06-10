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

import robustisoty as conns


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


class TeeTest(unittest.TestCase):

    def setUp(self):
        self.retval = "Hi"
        self.fs = [Mock(), Mock()]

    def test_functions_all_success(self):
        for f in self.fs:
            f.return_value = self.retval

        fproxy = conns.Tee(self.fs)
        self.assertEqual(fproxy(), self.retval)

    def test_objects_all_success(self):
        for f in self.fs:
            f.foo.return_value = self.retval

        fproxy = conns.Tee(self.fs)
        self.assertEqual(fproxy.foo(), self.retval)

    def test_objects_first_returns_none(self):
        self.fs[0].foo.return_value = None
        self.fs[1].foo.return_value = self.retval

        fproxy = conns.Tee(self.fs)
        self.assertEqual(fproxy.foo(), None)

    def test_attrs_all_success(self):
        for f in self.fs:
            f.foo = self.retval

        fproxy = conns.Tee(self.fs)
        self.assertEqual(fproxy.foo, self.retval)

    def test_attrs_first_fails(self):
        class Fake(object):
            def __getattr__(self, *args):
                raise Exception()

        self.fs[0] = Fake()
        self.fs[1].foo = self.retval

        self.assertEqual(conns.Tee(self.fs).foo, self.retval)

    def test_attrs_second_fails(self):
        class Fake(object):
            def __getattr__(self, *args):
                raise Exception()

        self.fs[0].foo = self.retval
        self.fs[1] = Fake()
        self.assertEqual(conns.Tee(self.fs).foo, self.retval)

    def test_attrs_all_fails(self):
        class Fake(object):
            def __getattr__(self, *args):
                raise Exception()

        self.assertRaises(Exception, getattr, conns.Tee([Fake(), Fake()]),
                          'foo')

    def test_first_fails(self):
        self.fs[0].foo.side_effect = Exception
        self.fs[1].foo.return_value = self.retval
        self.assertEqual(conns.Tee(self.fs).foo(), self.retval)

    def test_second_fails(self):
        self.fs[0].foo.return_value = self.retval
        self.fs[1].foo.side_effect = Exception
        self.assertEqual(conns.Tee(self.fs).foo(), self.retval)

    def test_all_fail(self):
        for f in self.fs:
            f.foo.side_effect = Exception

        self.assertRaises(Exception, conns.Tee(self.fs).foo)

    def test_dicts_both_succeed(self):
        self.assertEqual(conns.Tee([{'foo': self.retval},
                                    {'foo': self.retval}])['foo'],
                         self.retval)


if __name__ == '__main__':
    unittest.main()
