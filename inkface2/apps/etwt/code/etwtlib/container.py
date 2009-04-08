
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

        if other is None:
            return self

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

        self.cur_bbox = None
        self.widgets = []
        self.index = 0
        self.anim_period = 10

        self.bbox = BoundingBox(bbox)
        self.upArrow_elem = upArrow_elem
        self.upArrow_elem.onLeftClick = self.onUpArrow
        self.downArrow_elem = downArrow_elem
        self.downArrow_elem.onLeftClick = self.onDownArrow

    def add(self, widget):
        self.widgets.append(widget)

        wbbox = BoundingBox(widget.get_bounding_box())
        
        self.cur_bbox = wbbox + self.cur_bbox

        return not (self.cur_bbox <= self.bbox)
            

    def remove(self, widget):
        self.widgets.remove(widget)

    def upAnimate(self, elem):
        x,y = elem.get_position()

        if elem.anim_length < self.anim_step:
            elem.set_position((x, y-elem.anim_length))
            elem.refresh(svg_reload=False)
            elem.anim_length = 0
            elem.onDraw = None
            return False
        else:
            elem.set_position((x, y-self.anim_step))
            elem.refresh(svg_reload=False)
            elem.anim_length -= self.anim_step
            return True

    def onUpArrow(self, elem):

        _,_,_,wh = self.widgets[self.index].get_bounding_box()
        self.anim_step = wh / self.anim_period
        self.widgets[self.index].hide()

        self.anim_length = wh

        self.index += 1

        visible_widgets = self.widgets[self.index:]

        bb = None
        for w in visible_widgets:
            bb = BoundingBox(w.get_bounding_box()) + bb
        
        # TODO make it while
        if bb <= self.bbox:
            self.emit('request')
                            
        for vw in self.widgets[self.index:]:
            vw.text_elem.anim_length = self.anim_length
            vw.text_elem.onDraw = self.upAnimate
            vw.background_elem.anim_length = self.anim_length
            vw.background_elem.onDraw = self.upAnimate
            vw.image_elem.anim_length = self.anim_length
            vw.image_elem.onDraw = self.upAnimate


    def onDownArrow(self, elem):
        print 'going down'


if __name__ == '__main__':
    b1 = BoundingBox((10,10,90,90))
    b2 = BoundingBox((0,30,10,10))

    print b2 <= b1  # Should be False
