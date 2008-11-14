#!/usr/bin/env python

import unittest

import sys
import os
import inkface


class TestSVGLoad(unittest.TestCase):
    arbit_ids = ('#g3509','#g3359','#rect2660','#g3434','#g3316')
    arbit_names = ('keyO','keyPGlow','exitDoor','background','keyDGlow')

    def setUp(self):
        self.SVG = os.path.join(sys.argv[1])
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
        canvas = inkface.create_X_canvas()
        self.assert_(canvas.width > 0)
        self.assert_(canvas.height > 0)
        self.assert_(canvas.fullscreen == False)
            
    def testCanvasInitAllParams(self):
        canvas = inkface.create_X_canvas(width=10,height=10,fullscreen=True)
        self.assert_(canvas.width == 10)
        self.assert_(canvas.height == 10)
        self.assert_(canvas.fullscreen == True)

    def testCanvasInitSomeParams(self):
        canvas = inkface.create_X_canvas(fullscreen=True)
        self.assert_(canvas.width > 0)
        self.assert_(canvas.height > 0)
        self.assert_(canvas.fullscreen == True)

    def testCanvasInitFullscreen(self):
        import os
        os.environ['INKFACE_FULLSCREEN'] = 'TRUE'
        canvas = inkface.create_X_canvas()
        self.assert_(canvas.fullscreen == True)

        del os.environ['INKFACE_FULLSCREEN']
        canvas = inkface.create_X_canvas()
        self.assert_(canvas.fullscreen == False)

class TestCanvasElements(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(sys.argv[1])
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.create_X_canvas()
        
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
        self.SVG = os.path.join(sys.argv[1])
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.create_X_canvas()

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

class TestCallbackExceptions(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(sys.argv[1])
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.create_X_canvas()
        self.canvas.register_elements(self.elements)
        for e in self.elements:
            if e.name == 'exitDoor':
                e.onKeyPress = self.bad_callback
                e.onMouseEnter = self.bad_callback

    def bad_callback():
        pass

    def testEventHandlerExceptions(self):
        print 'Press actual keyboard key'
        self.assertRaises(TypeError,self.canvas.eventloop)
        print 'Move the mouse over the exit door'
        self.assertRaises(TypeError,self.canvas.eventloop)
        inkface.exit()
        

if __name__ == '__main__':
    for t in [TestSVGLoad,TestCanvas,TestCanvasElements,\
                TestElements,TestCallbackExceptions]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=0).run(suite)
