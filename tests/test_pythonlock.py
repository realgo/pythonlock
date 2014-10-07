#!/usr/bin/env python
#
#  Test of pythonlock code.
#
#===============
#  This is based on a skeleton test file, more information at:
#
#     https://github.com/linsomniac/python-unittest-skeleton

import unittest

import os
import sys
import tempfile
import glob
sys.path.append('..')
import pythonlock


class test_PythonLock_Basic(unittest.TestCase):
    def setUp(self):
        self.lockfile_name = tempfile.mktemp(prefix='pythonlock-test-')

    def tearDown(self):
        for filename in glob.glob('%s*' % self.lockfile_name):
            if os.path.exists(filename):
                os.remove(filename)

    def test_Basic(self):
        self.assertFalse(os.path.exists(self.lockfile_name))
        lock_1 = pythonlock.lock(self.lockfile_name)
        self.assertEqual(lock_1.have_lock, True)
        self.assertTrue(os.path.exists(self.lockfile_name))

        lock_2 = pythonlock.lock(self.lockfile_name)
        self.assertEqual(lock_2.have_lock, False)

        lock_1.release()
        self.assertEqual(lock_1.have_lock, False)
        self.assertFalse(os.path.exists(self.lockfile_name))

        lock_2 = pythonlock.lock(self.lockfile_name)
        self.assertEqual(lock_2.have_lock, True)
        self.assertTrue(os.path.exists(self.lockfile_name))
        lock_2.release()
        self.assertEqual(lock_2.have_lock, False)
        self.assertFalse(os.path.exists(self.lockfile_name))

unittest.main()
