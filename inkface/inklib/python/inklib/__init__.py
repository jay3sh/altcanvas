'''Python library on top of inkface-python bindings'''

import inkface
import sys

class Face:
    def resultProcessor(self,**params):
        pass

    def __init__(self,canvas,svgname,autoload=True):
        assert(canvas)
        self.canvas = canvas

        if autoload:
            self.elements = inkface.loadsvg(svgname) 
            for name,elem in self.elements.items():
                self.__dict__[name] = elem

    def wire(self):
        print 'This method should be overloaded by '+str(self.__class__)

    def unwire(self):
        for elem in self.elements.values():
            elem.onMouseEnter = None
            elem.onMouseLeave = None
            elem.onTap = None
            elem.onKeyPress = None
            elem.onDraw = None
        self.resultProcessor = None

 
    def __del__(self):
        print '__del__'+str(self.__class__)
        for name,elem in self.elements.items():
            del self.__dict__[name]
        inkface.unload(self.elements); 
