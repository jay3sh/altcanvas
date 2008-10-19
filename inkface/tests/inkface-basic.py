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
        
class TestCanvas(unittest.TestCase):
    def setUp(self):
        pass

    def testCanvasInitNoParams(self):
        canvas = inkface.canvas()
        self.assert_(canvas.width > 0)
        self.assert_(canvas.height > 0)
        self.assert_(canvas.fullscreen == False)
            
    def testCanvasInitAllParams(self):
        canvas = inkface.canvas(width=10,height=10,fullscreen=True)
        self.assert_(canvas.width == 10)
        self.assert_(canvas.height == 10)
        self.assert_(canvas.fullscreen == True)

    def testCanvasInitSomeParams(self):
        canvas = inkface.canvas(fullscreen=True)
        self.assert_(canvas.width > 0)
        self.assert_(canvas.height > 0)
        self.assert_(canvas.fullscreen == True)

    def testCanvasInitFullscreen(self):
        import os
        os.environ['INKFACE_FULLSCREEN'] = 'TRUE'
        canvas = inkface.canvas()
        self.assert_(canvas.fullscreen == True)

        del os.environ['INKFACE_FULLSCREEN']
        canvas = inkface.canvas()
        self.assert_(canvas.fullscreen == False)

    def testCanvasTimer(self):
        canvas = inkface.canvas()
        canvas.set_timer(160) # msec
        # Assuming REFRESH_INTERVAL_MSEC = 50 msec 
        self.assert_(canvas.timer_step == 3)

class TestCanvasElements(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'keyboard.svg')
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.canvas()
        
    def testRegisterUnregisterNothing(self):
        self.assertRaises(ValueError,self.canvas.register_elements)
        self.assertRaises(ValueError,self.canvas.unregister_elements)

    def testRegisterUnregister(self):
        self.canvas.register_elements(self.elements)
        self.assert_(len(self.canvas.elements) ==
                        len(self.elements))
        self.canvas.unregister_elements(self.elements)
        # TODO: self.assert_(len(self.elements) == 0)
        
class TestElements(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'keyboard.svg')
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.canvas()

    def testHandlerRegistration(self):
        def onEvent(x,y):
            pass
        for e in self.elements:
            self.assert_(e.onTap == None)
            self.assert_(e.onMouseEnter == None)
            self.assert_(e.onMouseLeave == None)
            self.assert_(e.onDraw == None)

            e.onTap = onEvent
            e.onMouseEnter = onEvent
            e.onMouseLeave = onEvent
            e.onDraw = onEvent

            self.assert_(e.onTap)
            self.assert_(e.onMouseEnter)
            self.assert_(e.onMouseLeave)
            self.assert_(e.onDraw)


if __name__ == '__main__':
    for t in [TestSVGLoad,TestCanvas,TestCanvasElements,TestElements]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=0).run(suite)
