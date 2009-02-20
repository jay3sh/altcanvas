

import cairo

def TRACE(str):
    print str


def __getattr__(attrname):
    TRACE('Accessing cairo.'+attrname) 
    return cairo.__dict__[attrname]

class ImageSurface:
    def __init__(self,*args,**kwds):
        TRACE('Creating <ImageSurface> ('+str(args)+str(kwds)+')')
        self.__imageSurface = cairo.ImageSurface(self,args,kwds)

class Context:
    def __init__(self,*args,**kwds):
        TRACE('Creating <Context> ('+str(args)+str(kwds)+')')
        self.__context = cairo.Context(args,kwds)

    def __getattr__(self,attrname):
        TRACE('Accessing Context.'+attrname)
        return self.__context.__dict__[attrname]


