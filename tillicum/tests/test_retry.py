# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for tillicum.retry."""

import unittest

from tillicum.retry import retry

class RetryTest(unittest.TestCase):

    def test_is_decorator(self):
        self.assertTrue(callable(retry(lambda: None)))

    def test_retries_once(self):
        calls = []
        def lossy():
            if not calls:
                calls.append(1)
                raise ValueError("Blah")
            return 42

        f = retry(exceptions=ValueError)(lossy)
        self.assertEqual(f(), 42)
        self.assertEqual(len(calls), 1)

    def test_raises_when_fails(self):
        calls = []
        def lossy():
            calls.append(1)
            raise ValueError("Blah")

        f = retry(4, exceptions=ValueError)(lossy)
        self.assertRaises(ValueError, f)
        self.assertEqual(len(calls), 4)



if __name__ == '__main__':
    unittest.main()
