#!/usr/bin/env python

import unittest

import sys
import os
import inkface
from time import sleep

canvas = None

flags = {
        'topTouch':0,
        'bottomTouch':0,
        'leftTouch':0,
        'rightTouch':0
    }

def onMouseEnter(element,elist):
    global flags
    flags[element.name] = 1
    canvas.refresh()

def onDraw(element):
    global canvas
    global flags
    if flags[element.name] == 0:
        canvas.draw(element)

def onMouseLeave(element,elist):
    global flags
    if 0 not in flags.values():
        canvas.cleanup()
        sys.exit(1)

def main():
    global canvas
    svg = os.path.join(sys.argv[1])
    elements = inkface.loadsvg(svg)
    canvas = inkface.canvas()
    canvas.register_elements(elements)

    text_arr = []
    for elem in elements:
        if elem.text:
            text_arr.append(elem.text)
            if elem.text == 'inkface':
                elem.text = '(-- '+elem.text+' --)'
                elem.refresh()

        if elem.name.endswith('Touch'):
            elem.onDraw = onDraw
            elem.onMouseLeave = onMouseLeave
            elem.onMouseEnter = onMouseEnter

    if 'inkface' not in text_arr:
        print 'Text validation test failed'
        sys.exit(1)

    canvas.show()
    canvas.eventloop()

    
if __name__ == '__main__':
    main()

   
