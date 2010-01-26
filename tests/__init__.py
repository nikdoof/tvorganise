import unittest
import testtvorganise

def all():
    
    suite = unittest.TestSuite()

    testtvorganise.suite(suite)

    return suite

