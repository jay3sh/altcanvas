#!/usr/bin/python

import sys
import os

import inkface

import clutter
import cluttercairo
import cairo


class Face:
    def __init__(self,svgname,autoload=True):
        assert(os.path.exists(svgname))
        if autoload:
            self.elements = inkface.loadsvg(svgname) 
            for name,elem in self.elements.items():
                self.__dict__[name] = elem

    def __del__(self):
        for name,elem in self.elements.items():
            del self.__dict__[name]
        inkface.unload(self.elements); 


def main():
    f = Face(svgname='paths.svg')
    print f.path0.d


if __name__ == '__main__':
    main()

