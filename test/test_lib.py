#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sys
#import unittest
import unittest2 as unittest

sys.path.append(path.split(path.dirname(path.abspath(__file__)))[0])

import lib

class test_lib(unittest.TestCase):

    def test_endpoint_class(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    unittest.main()
