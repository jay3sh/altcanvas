#!/usr/bin/env python

import unittest

import sys
import os
import inkface
from time import sleep

TEST_DATA_DIR = sys.argv[1]


class TestShow(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'keyboard.svg')
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.canvas()
        self.canvas.register_elements(self.elements)

    def testShow(self):
        self.canvas.show()
        sleep(2)
        
if __name__ == '__main__':
    for t in [TestShow]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)
