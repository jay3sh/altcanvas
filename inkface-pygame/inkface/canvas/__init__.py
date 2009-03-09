
import sys
import unittest
import pygame
from inkface.altsvg.element import Element

class Face:
    svg = None
    svgelements = []

    def __init__(self,svgname,autoload=True):
        from inkface.altsvg import VectorDoc
        self.svg = VectorDoc(svgname)
        self.svgelements = self.svg.get_elements()

class PygameFace(Face):
    elements = []

    def __init__(self,svgname):
        Face.__init__(self,svgname)

        for svge in self.svgelements:
            pElement = PygameCanvasElement(svge)
            try:
                self.__dict__[svge.label] = pElement 
            except AttributeError, ae:
                pass

            self.elements.append(pElement)

    def get(self,key):
        try:
            return self.__dict__[key] 
        except AttributeError,ae:
            pass

        return None

    def clone(self, curNodeName, newNodeName, new_x=-1, new_y=-1):

        if not self.__dict__.has_key(curNodeName):
            raise Exception(curNodeName+' does not exist for cloning')

        if curNodeName == newNodeName:
            raise Exception('New node should have different name')

        curNode = self.__dict__[curNodeName]

        newNode = curNode.dup(newNodeName)

        if new_x > 0: newNode._x = new_x
        if new_y > 0: newNode._y = new_y

        curNodePos = self.elements.index(curNode)
        self.elements.insert(curNodePos+1,newNode)
        self.__dict__[newNodeName] = newNode

class CanvasElement:
    def __init__(self,svgelem):
        self.svg = svgelem
        self.clouds = []

        self.onLeftClick = None
        self.onRightClick = None
        self.onTap = None
        self.onMouseOver = None
        self.onKeyPress = None

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


class PygameCanvasElement(CanvasElement):

    class ElementSprite(pygame.sprite.DirtySprite):
        def __init__(self,parent):
            pygame.sprite.DirtySprite.__init__(self)
            self.parent = parent

        def update(self,*args):
            if self.parent.onDraw != None:
                self.parent.onDraw(self.parent)

    def set_position(self, (x, y)):
        CanvasElement.set_position(self, (x, y))
        self.sprite.rect.center = (self._x + self.svg.w/2, \
                                    self._y + self.svg.h/2)
        if self.sprite.visible == 1:
            self.sprite.dirty = 1
        
    def hide(self):
        if self.sprite.visible == 1:   
            self.sprite.visible = 0
            self.sprite.dirty = 1

    def unhide(self):
        if self.sprite.visible == 0:
            self.sprite.visible = 1
            self.sprite.dirty = 1
        
    def _ARGBtoRGBA(self,str_buf):
        # cairo's ARGB is interpreted by pygame as BGRA due to 
        # then endian-format difference this routine swaps B and R 
        # (0th and 2nd) byte converting it to RGBA format.
        import array
        byte_buf = array.array("c", str_buf)
        num_quads = len(byte_buf)/4
        for i in xrange(num_quads):
            tmp = byte_buf[i*4 + 0]
            byte_buf[i*4 + 0] = byte_buf[i*4 + 2]
            byte_buf[i*4 + 2] = tmp
        return byte_buf

    def __init__(self,svgelem):
        CanvasElement.__init__(self,svgelem)
        self.sprite = self.ElementSprite(self)
        self.refresh()

    def refresh(self,svg_reload=False):
        if svg_reload or self.svg.surface == None:
            self.svg.render()
        buf = self._ARGBtoRGBA(self.svg.surface.get_data())
        image = pygame.image.frombuffer(buf.tostring(),
                    (self.svg.surface.get_width(),
                    self.svg.surface.get_height()),"RGBA")
        self.sprite.image = image
        self.sprite.rect = image.get_rect()
        self.sprite.rect.center = (self._x + self.svg.w/2, \
                                    self._y + self.svg.h/2)
        self.sprite.dirty = 1

    def dup(self, newName):
        # Clone the svg element first, it has to be a new instance and not
        # just a new reference to the same svg element
        # The new instance's SVG attributes should be changeable without
        # affecting the original svg element

        import xml.etree.ElementTree
        node_str = xml.etree.ElementTree.tostring(self.svg.node)
        new_node = xml.etree.ElementTree.fromstring(node_str)
        new_svg = Element(new_node,self.svg.vdoc)
        new_svg.label = newName
        return PygameCanvasElement(new_svg)
        
       

    
class Canvas:
    elementQ = [] 
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

import threading

class PygameCanvas(Canvas):
    animateflag = False
    def __init__(self,
                resolution = (640,480),
                caption='Inkface App',
                framerate=25):

        Canvas.__init__(self)

        resolution = map(lambda x: int(x), resolution)

        pygame.init()
        self.screen = pygame.display.set_mode(resolution,pygame.DOUBLEBUF)
        self.dispsurf = pygame.Surface(self.screen.get_size())
        self.dispsurf.convert()
        pygame.display.set_caption(caption)

        self.elem_group = pygame.sprite.LayeredDirty(
                            _use_update=True, _time_threshold=1000./framerate)
        #self.passive_elem_group = pygame.sprite.LayeredDirty()

        self.framerate = framerate
        if self.framerate > 0:
            self.clock = pygame.time.Clock()
            self.painter = self._PainterThread(self)
            self.painter.start()

    class _PainterThread(threading.Thread):
        def __init__(self,canvas):
            threading.Thread.__init__(self)
            self.canvas = canvas
            self.stopflag = False
            self.framerate = 0
            self.maxcount = 0

        def run(self):
            while True:
                if self.stopflag: 
                    return

                self.canvas.clock.tick(self.canvas.framerate)

                self.canvas.paint()


        def stop(self):
            self.stopflag = True

    def paint(self):
        self.elem_group.update()

        rectlist = self.elem_group.draw(self.dispsurf)
        self.screen.blit(self.dispsurf,(0,0))
                    
        pygame.display.flip()

    def add(self,face):
        Canvas.add(self,face)
        for elem in face.elements:  
            self.elementQ.append(elem)
            self.elem_group.add(elem.sprite)
        self.recalculate_clouds()

    def update(self):
        self.elem_group.update()

    def _handle_event(self,event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            # do onClick
            for elem in self.elementQ:
                if elem.occupies(event.pos) and \
                    not elem.clouded(event.pos):

                    if event.button == 1 and elem.onLeftClick != None:
                        elem.onLeftClick(elem)
                    elif event.button == 3 and elem.onRightClick != None:
                        elem.onRightClick(elem)

        
        elif event.type == pygame.MOUSEMOTION:
            # do onTap
            for elem in self.elementQ:
                if elem.occupies(event.pos) and \
                    not elem.clouded(event.pos):

                    if elem.onTap != None:
                        elem.onTap(elem)

        elif event.type == pygame.MOUSEBUTTONUP:
            pass

        elif event.type == pygame.KEYDOWN:
            for elem in self.elementQ:
                # TODO put hasFocus logic
                if elem.onKeyPress != None:
                    elem.onKeyPress(elem, event)

        elif event.type == pygame.QUIT:
            self.stop()
            return True

        return False

    # TODO rename to cleanup
    def stop(self):
        self.stop_signal = True
        if self.painter != None:
            self.painter.stop()
            self.painter.join()

    def eventloop(self):
        while True:
            self.stop_signal = self._handle_event(pygame.event.wait())

            if self.stop_signal: 
                return

    
    
