#!/usr/bin/env python

import unittest

import sys
import os
import inkface
from time import sleep

TEST_DATA_DIR = sys.argv[1]


'''
class TestShow(unittest.TestCase):
    def setUp(self):
        self.SVG = os.path.join(TEST_DATA_DIR,'test1.svg')
        self.elements = inkface.loadsvg(self.SVG)
        self.canvas = inkface.canvas()
        self.canvas.register_elements(self.elements)

    def testTouch(self):
        top = 0
        def onTop():
            top = 1

        self.canvas.show()
        sleep(2)
        
if __name__ == '__main__':
    for t in [TestShow]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)
'''

flags = {
        'topTouch':0,
        'bottomTouch':0,
        'leftTouch':0,
        'rightTouch':0
    }

def onMouseEnter(element,elist):
    global flags
    print 'Mouse '+element.name
    flags[element.name] = 1
    canvas.refresh()

def onDraw(element,proxy):
    global flags
    print 'Draw '+element.name
    if(flags[element.name] == 0):
        canvas.draw(element);

def main():
    svg = os.path.join(TEST_DATA_DIR,'test1.svg')
    elements = inkface.loadsvg(svg)
    canvas = inkface.canvas()
    canvas.register_elements(elements)

    text_arr = []
    for elem in elements:
        if elem.text:
            text_arr.append(elem.text)
            if elem.text == 'inkface':
                elem.text = '(== '+elem.text+' ==)'
                elem.refresh()

        elem.register_mouse_enter_handler(onMouseEnter)
        if elem.name == 'leftTouch':
            elem.register_draw_handler(onDraw)

    if 'inkface' not in text_arr:
        print 'Text validation test failed'
        sys.exit(1)

    canvas.show()
    canvas.eventloop()

    
if __name__ == '__main__':
    main()

   
