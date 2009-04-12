'''

module:: inkface.canvas.canvas -- Generic Canvas Backend
=============================================================

:synopsis: This module contains Class definitions used for Generic Canvas Backend
'''


from inkface.altsvg.element import Element

class Face:
    '''
    This is the base class from which backend specific Face classes \
    should inherit.
       .. attribute:: svg
       A reference to the SVG doc :class:`inkface.altsvg.VectorDoc` \
       from which this face is loaded

    '''
    def __init__(self,svgname,autoload=True):
        from inkface.altsvg import VectorDoc
        self.svg = VectorDoc(svgname)
        self.svgelements = self.svg.get_elements()

        self.elements = []
        self._elements_dict = {}

        self.parent_canvas = None

    def _append(self, svge, element):
        try:
            self._elements_dict[svge.label] = element
        except AttributeError, ae:
            # For non-labeled elements we get this error
            pass

        self.elements.append(element)
 

    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self._elements_dict.has_key(key):
            return self._elements_dict[key]
        else:
            raise AttributeError('Unknown Attribute %s'%str(key))
            
    def get(self,key):
        '''
        Access the elements by name This method has same result as accessing \
        the element as Face's attribute.

        :param key: Name of element you are looking for.

        '''
        try:
            return self._elements_dict[key] 
        except AttributeError,ae:
            pass

        return None

    def clone(self, curNodeName, newNodeName, new_x=-1, new_y=-1):
        '''
        Clones an existing element of the face to create duplicate one. \
        This method should be called by backend specific sub-class

        :param curNodeName: name of existing element to be cloned
        :param newNodeName: name the new element should have
        :param new_x: [optional] x coord of new element
        :param new_y: [optional] y coord of new element
 
        '''
        if not self._elements_dict.has_key(curNodeName):
            raise Exception(curNodeName+' does not exist for cloning')

        if curNodeName == newNodeName:
            raise Exception('New node should have different name')

        curNode = self._elements_dict[curNodeName]

        newNode = curNode.dup(newNodeName)

        if new_x > 0: newNode._x = new_x
        if new_y > 0: newNode._y = new_y

        newNode.refresh()

        curNodePos = self.elements.index(curNode)
        self.elements.insert(curNodePos+1,newNode)
        self._elements_dict[newNodeName] = newNode



class CanvasElement:
    '''
    This is the base class from which backend specific CanvasElement classes \
    should inherit.
       .. attribute:: svg
       A reference to :class:`inkface.altsvg.element.Element` object
    '''
    def __init__(self,svgelem):
        self.svg = svgelem
        self.clouds = []

        self.onLeftClick = None
        self.onMiddleClick = None
        self.onRightClick = None
        self.onTap = None
        self.onMouseOver = None
        self.onKeyPress = None
        self.onGainFocus = None
        self.onLoseFocus = None
        self.onMouseGainFocus = None
        self.onMouseLoseFocus = None

        self.onDraw = None

        self._x = self.svg.x
        self._y = self.svg.y

    def set_position(self, (x, y)):
        '''
        :param (x,y): x,y coordinates to set this element's position to
        '''
        self._x = x
        self._y = y

    def get_position(self):
        '''
        :rtype: A tuple giving (x,y) coordinates.
        '''
        return (self._x, self._y)

    def occupies(self,(x,y)):
        '''
        :rtype: True if this element occupies given coordinates (x, y), \
        False otherwise. Typically useful to event processing \
        logic of a backend specific subclass.
        '''
        return ((x > self._x) and (y > self._y) and \
                (x < self._x+self.svg.w) and (y < self._y+self.svg.h))

    def clouded(self,(x,y)):
        '''
        :rtype: True if this element is clouded by other elements at these \
        coordinates. False otherwise. Typically useful to event processing \
        logic of a backend specific subclass.
        '''
        rx = x - self._x
        ry = y - self._y

        for cloud in self.clouds:
            cx0, cy0, cx1, cy1 = cloud 
            if ((rx > cx0) and (rx < cx1) and (ry > cy0) and (ry < cy1)):
                return True

        return False

    def dup(self, newName):
        '''
        This is a virtual method, to be implemented by backend specific \
        subclass.
        '''
        raise Exception('This method should be overridden by subclass')

class Canvas:
    '''
    This is the base class from which backend specific Canvas classes should inherit.
    '''
 
    elementQ = [] 
    focusElement = None

    def __init__(self):
        pass

    def recalculate_clouds(self):
        '''
        Recalculate the clouds for all elements in the elementQ.
        '''
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
        '''
        Adds the elements of the face to the internal elementQ.

        :param face: Face whose elements are to be added.
        '''
        for elem in face.elements:  
            self.elementQ.append(elem)
        self.recalculate_clouds()

    def insert_after(self, existing_elem, new_elem):
        i = 0
        for elem in self.elementQ:
            if elem is existing_elem:
                self.elementQ.insert(i+1, new_elem)
                break
            i += 1
        self.recalculate_clouds()

    def remove(self, face):
        '''
        Removes the elements of the face from internal elementQ.

        :param face: Face whose elements are to be removed.
        '''
        for elem in face.elements:
            self.elementQ.remove(elem)


      


