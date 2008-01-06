
import unittest
import sys
import os

import libpub.imagic

class PresenceTest(unittest.TestCase):
    def setUp(self):
        self.imageMagick = libpub.imagic.ImageMagick()
    
    def testPresence(self):
        self.assert_(self.imageMagick.present())
        
class conversionTests(unittest.TestCase):
    def setUp(self):
        self.imageMagick = libpub.imagic.ImageMagick()
        
        if sys.platform.find('win32') >= 0:
            self.origsvg = 'C:\\Documents and Settings\\jayesh\\Desktop\\publishr-folder\\test1.svg'
            self.origimg = 'C:\\Documents and Settings\\jayesh\\Desktop\\publishr-folder\\test2.jpg'
        else:
            self.origsvg = '/home/jayesh/trunk/altcanvas/tests/data/test1.svg'
            self.origimg = '/home/jayesh/trunk/altcanvas/tests/data/test2.jpg'
        
    def testSVG2JPG(self):
        jpegfile = self.imageMagick.svg2jpeg(self.origsvg)
        self.assert_(jpegfile)
        try:
            fd = open(jpegfile)
            fd.close()
        except IOError, ioe:
            fail('Failed to access jpegfile: %s'%ioe)
    
    def testIMG2THUMB(self):
        thumbfile = self.imageMagick.img2thumb(self.origimg,"100x100")
        self.assert_(thumbfile)
        try:
            fd = open(thumbfile)
            fd.close()
        except IOError, ioe:
            self.fail('Failed to access thumbfile: %s'%ioe)
            
        geometry = self.imageMagick.getImageGeometry(thumbfile)
        self.assert_(geometry.find('100') >= 0)
            

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(PresenceTest)
    presenceTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
    
    if not presenceTestResult:
        sys.exit()
        
    suite = unittest.TestLoader().loadTestsFromTestCase(conversionTests)
    conversionTestResult = unittest.TextTestRunner(verbosity=2).run(suite)
