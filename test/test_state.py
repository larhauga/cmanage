#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sys
#import unittest
import unittest2 as unittest

sys.path.append(path.split(path.dirname(path.abspath(__file__)))[0])

from lib import state

class test_state(unittest.TestCase):

    def setUp(self):
        pass

    def test_state_class(self):
        pass
        #name = "hest"
        #self.assertRaises(TypeError, state.state)
        #self.assertEqual(type(state.state), state.state(name))

if __name__ == '__main__':
    unittest.main()
