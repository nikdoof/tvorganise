#!/usr/bin/env python
#encoding:utf-8

import tvorganise
import unittest
import os
import shutil
import tempfile

class testTvOrganise(unittest.TestCase):
    """
    Test class for TvOrganise module
    """

    def testConfigParser(self):
        """
        Simple test to check to see if the config parser actually returns a
        dict on completion
        """
        dict = self.tvo._get_config('tvorganise.cfg')
        self.assertTrue(dict)

    def testConfigSettings(self):
        """
        Using a predefined dict, save then load the config and validate 
        the contents
        """
        pass

    def setUp(self):
        self.tvo = tvorganise.TvOrganiser()


class testFindFiles(unittest.TestCase):
    """
    Test find_files() function
    """

    def setUp(self):
        os.makedirs("/tmp/find-files-test/folder1")
        os.makedirs("/tmp/find-files-test/folder2")

	open('/tmp/find-files-test/folder1/file1', 'w').close() 
        open('/tmp/find-files-test/folder1/file2', 'w').close()
        open('/tmp/find-files-test/folder2/file3', 'w').close()
        open('/tmp/find-files-test/folder2/file4', 'w').close()
        open('/tmp/find-files-test/folder2/file5', 'w').close()

    def tearDown(self):
        shutil.rmtree("/tmp/find-files-test/")        

    def testFolderList(self):
        self.assertEqual(len(tvorganise.find_files("/tmp/find-files-test/")),5)
        self.assertEqual(len(tvorganise.find_files("/tmp/find-files-test/folder1")),2)
        self.assertEqual(len(tvorganise.find_files("/tmp/find-files-test/folder2")),3)

    def testMultipleInput(self):
        input = ['/tmp/find-files-test/folder1/', '/tmp/find-files-test/folder2/']
        self.assertEqual(len(tvorganise.find_files(input)),5)

    def testCrapInput(self):
        self.assertEqual(len(tvorganise.find_files("belfrhe")),0)

def suite(suite=None):

    if not suite:
        suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(testTvOrganise))
    suite.addTest(unittest.makeSuite(testFindFiles))
 
    return suite

def run():
    unittest.TextTestRunner(verbosity=2).run(suite())

