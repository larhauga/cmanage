import unittest2
from os import path

loader = unittest2.TestLoader()

tests = loader.discover(path.dirname(path.abspath(__file__)))
testRunner = unittest2.runner.TextTestRunner()
testRunner.run(tests)
