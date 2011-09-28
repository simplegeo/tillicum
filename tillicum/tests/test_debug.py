# -*- coding: utf-8 -*-
#
# © 2011 SimpleGeo, Inc. All rights reserved.
# Author: Ian Eure <ian.eure@gmail.com>
#

"""Tests for tillicum.debug."""

import unittest
import pdb
import signal

from tillicum.test_tools import patch_object
from mock import Mock
import tillicum.debug as dbg


class DebugOnExceptionTest(unittest.TestCase):

    def test_get_debugger(self):
        self.assertTrue(isinstance(dbg.debug_on_exception().get_debugger(),
                                   pdb.Pdb))

    def test_decorator(self):
        f = lambda: None
        f_ = dbg.debug_on_exception()(f)
        self.assertTrue(callable(f_))
        self.assertEqual(f_(), None)

    def test_context_manager(self):
        with dbg.debug_on_exception():
            self.assertTrue(True)

    def test_ignores_other_exceptions(self):
        def raises_():
            return {}['x']

        self.assertRaises(KeyError,
                          dbg.debug_on_exception(ValueError)(raises_))

    def test_enters_debugger(self):
        def raises_():
            return {}['x']

        deco = dbg.debug_on_exception(KeyError)
        debugger = Mock()
        with patch_object(deco, 'get_debugger') as pdb:
            pdb.return_value = debugger
            self.assertRaises(KeyError, deco(raises_))

        self.assertTrue(debugger.reset.called)
        self.assertTrue(debugger.interaction.called)


class LetSignalTest(unittest.TestCase):

    def test_saves_handler(self):
        handler = lambda signum, frame: None
        with patch_object(dbg.signal, 'signal') as sig:
            mgr = dbg._let_signal(signal.SIGALRM, handler)
            mgr.__enter__()
            self.assertTrue(sig.call_args[0] == (signal.SIGALRM, handler))

    def test_restores_handler(self):
        handler_1 = lambda signum, frame: None
        handler_2 = lambda s, f: True
        with dbg._let_signal(signal.SIGALRM, handler_1):
            with dbg._let_signal(signal.SIGALRM, handler_2):
                self.assertEqual(signal.getsignal(signal.SIGALRM), handler_2)

            self.assertEqual(signal.getsignal(signal.SIGALRM), handler_1)


class DebugOnSignalTest(unittest.TestCase):

    def test_sets_and_restores_handler(self):
        old_h = signal.getsignal(signal.SIGHUP)
        mgr = dbg.debug_on_signal(signal.SIGHUP)
        with mgr:
            self.assertEqual(signal.getsignal(signal.SIGHUP), mgr._handler)
        self.assertEqual(signal.getsignal(signal.SIGHUP), old_h)

    def test_handler_enters_debugger(self):
        mgr = dbg.debug_on_signal(signal.SIGHUP)
        debugger = Mock()
        with patch_object(mgr, 'get_debugger') as pdb:
            pdb.return_value = debugger
            fake_frame = Mock()
            mgr._handler(signal.SIGHUP, fake_frame)

        self.assertTrue(debugger.set_trace.called)

if __name__ == '__main__':
    unittest.main()
