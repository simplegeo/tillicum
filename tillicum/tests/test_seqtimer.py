# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for tillicum.seqtimer."""

import unittest
from StringIO import StringIO

import tillicum.seqtimer as st
from tillicum.test_tools import patch_object


class SeqTimerTest(unittest.TestCase):

    def test_passthrough(self):
        items = range(100)
        out = StringIO()
        seq = st.seqtimer(items, items=10, output=out, summary=False)
        for (idx, item) in enumerate(seq):
            self.assertEqual(items[idx], item)

        self.assertEqual(len(out.getvalue().split("\n")), 11)

    def test_warns(self):
        # def generic_iter(inp):
        #     for elt in inp:
        #         yield elt

        out = StringIO()
        seq = st.seqtimer(iter(range(10)), output=out, summary=False,
                          length=1)
        with patch_object(st.warnings, 'warn') as warn:
            for (idx, item) in enumerate(seq):
                pass
        self.assertTrue(warn.called)

if __name__ == '__main__':
    unittest.main()
