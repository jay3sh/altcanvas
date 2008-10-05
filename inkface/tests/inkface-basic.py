#!/usr/bin/env python

import unittest

import sys
import os
import inkface

TEST_DATA_DIR = sys.argv[1]

class TestSVGLoad(unittest.TestCase):
    arbit_ids = ('#g3509','#g3359','#rect2660','#g3434','#g3316')
    arbit_names = ('keyO','keyPGlow','exitDoor','background','keyDGlow')

    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'keyboard.svg')
        self.elements = inkface.loadsvg(self.SVG)

    def testLoad(self):
        self.assert_(len(self.elements) == 54)

    def testIdPresence(self):
        svg_ids = map(lambda x: x.id, self.elements)
        for id in self.arbit_ids:
            self.assert_(id in svg_ids)
        
    def testNamePresence(self):
        svg_names = map(lambda x: x.name, self.elements)
        for name in self.arbit_names:
            self.assert_(name in svg_names)
        
            

if __name__ == '__main__':
    for t in [TestSVGLoad]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)
