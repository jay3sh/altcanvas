

from inkface.altsvg.element import Element

class Face:
    svg = None
    svgelements = []

    def __init__(self,svgname,autoload=True):
        from inkface.altsvg import VectorDoc
        self.svg = VectorDoc(svgname)
        self.svgelements = self.svg.get_elements()


class CanvasElement:
    def __init__(self,svgelem):
        self.svg = svgelem
        self.clouds = []

        self.onLeftClick = None
        self.onRightClick = None
        self.onTap = None
        self.onMouseOver = None
        self.onKeyPress = None
        self.onGainFocus = None
        self.onLoseFocus = None

        self.onDraw = None

        self._x = self.svg.x
        self._y = self.svg.y

    def set_position(self, (x, y)):
        self._x = x
        self._y = y

    def get_position(self):
        return (self._x, self._y)

    def occupies(self,(x,y)):
        return ((x > self._x) and (y > self._y) and \
                (x < self._x+self.svg.w) and (y < self._y+self.svg.h))

    def clouded(self,(x,y)):
        rx = x - self._x
        ry = y - self._y

        for cloud in self.clouds:
            cx0, cy0, cx1, cy1 = cloud 
            if ((rx > cx0) and (rx < cx1) and (ry > cy0) and (ry < cy1)):
                return True

        return False

class Canvas:

    elementQ = [] 
    focusElement = None

    def __init__(self):
        pass

    def recalculate_clouds(self):
        # Cleanup all the clouds before recalculating
        for e in self.elementQ:
            e.clouds = []
            
        for top in xrange(len(self.elementQ)):
        
            newElem = self.elementQ[top]
            newE = newElem.svg
            
            for i in xrange(top):
                oldElem = self.elementQ[i]
                oldE = oldElem.svg
                ox0 = oldE.x
                oy0 = oldE.y
                ox1 = ox0 + oldE.w
                oy1 = oy0 + oldE.h
               
                nx0 = newE.x
                ny0 = newE.y
                nx1 = nx0 + newE.w
                ny1 = ny0 + newE.h
                
                if (ox0 < nx0 and ox1 < nx0) or (ox0 > nx1 and ox1 > nx1) or \
                    (oy0 < ny0 and oy1 < ny0) or (oy0 > ny1 and  oy1 > ny1):
                    # There is no overlap
                    continue
                else:
                    '''
                    There is an overlap
                    Calculate the intersection of two widgets' extents
                    and add it to the cloud list of the old widget
                    Also translate them into widget's coordinate system
                    
                    These are top-left and bottom-right vertices of the rectangular
                    intersection of two widgets.
                    '''
                    oldElem.clouds.append((max(ox0,nx0)-ox0,
                                            max(oy0,ny0)-oy0,
                                            min(ox1,nx1)-ox0,
                                            min(oy1,ny1)-oy0))
 

    def add(self, face):
        pass

    def remove(self, face):
        pass


      


