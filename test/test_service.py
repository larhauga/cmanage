#!/usr/bin/env python
# -*- coding: utf-8 -*-

from os import path
import sys
#import unittest
import unittest2 as unittest

sys.path.append(path.split(path.dirname(path.abspath(__file__)))[0])

from lib import service

class test_service(unittest.TestCase):

    #def setUp(self):


    def test_service_class(self):
        name = "hest"
        self.assertRaises(TypeError, service.service)
        #self.assertEqual(type(service.service), service.service(name))

if __name__ == '__main__':
    unittest.main()
