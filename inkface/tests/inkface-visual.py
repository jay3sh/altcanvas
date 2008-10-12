#!/usr/bin/env python

import unittest

import sys
import os
import inkface
from time import sleep

TEST_DATA_DIR = sys.argv[1]
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


def main():
    global canvas
    svg = os.path.join(TEST_DATA_DIR,'test1.svg')
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

        elem.onMouseEnter = onMouseEnter
        if elem.name.endswith('Touch'):
            elem.onDraw = onDraw

    if 'inkface' not in text_arr:
        print 'Text validation test failed'
        sys.exit(1)

    canvas.show()
    canvas.eventloop()

    
if __name__ == '__main__':
    main()

   
