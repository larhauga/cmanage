#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sys
#import unittest
import unittest2 as unittest

sys.path.append(path.split(path.dirname(path.abspath(__file__)))[0])

from lib import endpoint

class test_endpoint(unittest.TestCase):

    #def setUp(self):


    def test_endpoint_class(self):
        name = "hest"
        self.assertRaises(TypeError, endpoint.endpoint)
        #self.assertEqual(type(endpoint.endpoint), endpoint.endpoint(name))

if __name__ == '__main__':
    unittest.main()
