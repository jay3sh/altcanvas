

from inkface.altsvg import TAG_INKSCAPE_LABEL

class Element:
    surface = None
    x = 0
    y = 0
    w = 0
    h = 0
    node = None

    def __init__(self,node,surface,x,y):
        self.node = node
        self.surface = surface
        self.x = x
        self.y = y
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self.node != None and key == 'label' and \
            self.node.attrib.has_key(TAG_INKSCAPE_LABEL):
            return self.node.attrib.get(TAG_INKSCAPE_LABEL)
        elif self.node != None and self.node.attrib.has_key(key):
            return self.node.attrib.get(key)

        raise AttributeError('Unknown attribute: '+key)


