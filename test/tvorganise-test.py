#!/usr/bin/env python
#encoding:utf-8

import tvorganise
import unittest
import os
import shutil

class testTvOrganise(unittest.TestCase):
    """
    Test class for TvOrganise module
    """

    def setUp(self):
        pass


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

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testTvOrganise))
    suite.addTest(unittest.makeSuite(testFindFiles))
 
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())

