
from etwtlib.inkobject import InkObject

class BoundingBox:
    def __init__(self, (x,y,w,h)=(0,0,0,0)):
        self.x, self.y, self.w, self.h = \
            x, y, w, h

    def __le__(self, other):
        return (self.x >= other.x and self.y >= other.x and \
            self.x+self.w <= other.x+other.w and \
            self.y+self.h <= other.y+other.h)
        
    def __add__(self, other):

        ox1, oy1, ox2, oy2 = \
            self.x, self.y, self.x+self.w, self.y+self.h
        nx1, ny1, nx2, ny2 = \
            other.x, other.y, other.x+other.w, other.y+other.h

        if nx1 < ox1: x1 = nx1
        else: x1 = ox1

        if ny1 < oy1: y1 = ny1
        else: y1 = oy1

        if nx2 > ox2: x2 = nx2
        else: x2 = ox2

        if ny2 > oy2: y2 = ny2
        else: y2 = oy2

        return BoundingBox((x1, y1, (x2-x1), (y2-y1)))

        
class Container(InkObject):
    def __init__(self, bbox,
        upArrow_elem, downArrow_elem):
        
        InkObject.__init__(self)

        self.cur_bbox = BoundingBox()
        self.widgets = []

        self.bbox = BoundingBox(bbox)
        self.upArrow_elem = upArrow_elem
        self.upArrow_elem.onLeftClick = self.onUpArrow
        self.downArrow_elem = downArrow_elem
        self.downArrow_elem.onLeftClick = self.onDownArrow

    def add(self, widget):
        self.widgets.append(widget)

        wbbox = BoundingBox(widget.get_bounding_box())
        
        self.cur_bbox = self.cur_bbox + wbbox

        return not (self.cur_bbox <= self.bbox)
            

    def remove(self, widget):
        self.widgets.remove(widget)

    def onUpArrow(self, elem):
        print 'going up'
                            

    def onDownArrow(self, elem):
        print 'going down'


if __name__ == '__main__':
    b1 = BoundingBox((10,10,90,90))
    b2 = BoundingBox((0,30,10,10))

    print b2 <= b1  # Should be False
