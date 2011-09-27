# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for ContextDecorator."""

import unittest

import tillicum.contextdecorator as cdec

class ContextDecoratorTest(unittest.TestCase):

    def test_works_as_decorator(self):
        class ContextManager(cdec.ContextDecorator):

            def __init__(self):
                self.enters = 0
                self.exits = []

            def __enter__(self):
                self.enters += 1

            def __exit__(self, *args):
                self.exits.append(args)
                return False


        f = lambda: 42

        f_ = ContextManager()
        self.assertEqual(f_(f)(), 42)
        self.assertEqual(f_.enters, 1)
        self.assertEqual(len(f_.exits), 1)

if __name__ == '__main__':
    unittest.main()
