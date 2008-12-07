'''Python library on top of inkface-python bindings'''

import inkface

class Face:
    def resultProcessor(self,**params):
        pass

    def __init__(self,canvas,svgname):
        assert(canvas)
        self.canvas = canvas
        self.elements = inkface.loadsvg(svgname) 
        for name,elem in self.elements.items():
            self.__dict__[name] = elem


 
