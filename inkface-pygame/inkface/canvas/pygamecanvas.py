
import pygame

from inkface.altsvg.element import Element

from inkface.canvas import Face
from inkface.canvas import CanvasElement

class PygameFace(Face):

    def __init__(self,svgname):
        Face.__init__(self,svgname)

        self.elements = []
        self._elements_dict = {}

        for svge in self.svgelements:
            pElement = PygameCanvasElement(svge)
            try:
                self._elements_dict[svge.label] = pElement 
            except AttributeError, ae:
                pass

            self.elements.append(pElement)

    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        elif self._elements_dict.has_key(key):
            return self._elements_dict[key]
        else:
            raise AttributeError('Unknown Attribute %s'%str(key))
            
    def get(self,key):
        try:
            return self._elements_dict[key] 
        except AttributeError,ae:
            pass

        return None

    def clone(self, curNodeName, newNodeName, new_x=-1, new_y=-1):

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

from inkface.canvas.canvas import Canvas
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
        Canvas.add(self, face)
        for elem in self.elementQ:
            self.elem_group.add(elem.sprite)

    def remove(self, face):
        Canvas.remove(self, face)
        for elem in self.elementQ:
            self.elem_group.add(elem.sprite)

    def update(self):
        self.elem_group.update()

    def _handle_event(self,event):

        if event.type == pygame.MOUSEBUTTONDOWN:
            # do onClick and adjust focus
            for elem in self.elementQ:
                if elem.occupies(event.pos) and \
                    not elem.clouded(event.pos):

                    # If the element is newly acquiring focus
                    # call relevant callback handlers
                    if self.focusElement != elem:
                        if self.focusElement != None and \
                            self.focusElement.onLoseFocus != None:
                            self.focusElement.onLoseFocus(elem)

                        if elem.onGainFocus != None:
                            elem.onGainFocus(elem)

                    self.focusElement = elem

                    # Call click callback handlers
                    if event.button == 1 and elem.onLeftClick != None:
                        elem.onLeftClick(elem)
                    elif event.button == 3 and elem.onRightClick != None:
                        elem.onRightClick(elem)

        
        elif event.type == pygame.MOUSEMOTION:
            # do onTap and adjust focus
            for elem in self.elementQ:
                if elem.occupies(event.pos) and \
                    not elem.clouded(event.pos):

                    # If the element is newly acquiring focus
                    # call relevant callback handlers
                    if self.focusElement != elem:
                        if self.focusElement != None and \
                            self.focusElement.onLoseFocus != None:
                            self.focusElement.onLoseFocus(elem)

                        if elem.onGainFocus != None:
                            elem.onGainFocus(elem)

                    self.focusElement = elem

                    # Call tap callback handlers
                    if elem.onTap != None:
                        elem.onTap(elem)

        elif event.type == pygame.MOUSEBUTTONUP:
            pass

        elif event.type == pygame.KEYDOWN:
            for elem in self.elementQ:
                if self.focusElement == elem and \
                    elem.onKeyPress != None:

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

       
 
