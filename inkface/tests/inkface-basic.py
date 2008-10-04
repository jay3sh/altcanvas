#!/usr/bin/env python

import unittest

import sys
import os
import inkface

TEST_DATA_DIR = sys.argv[1]

class TestSVGLoad(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'keyboard.svg')

    def testLoad(self):
        elements = inkface.loadsvg(self.SVG)
        self.assert_(len(elements) == 54)

if __name__ == '__main__':
    for t in [TestSVGLoad]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)
