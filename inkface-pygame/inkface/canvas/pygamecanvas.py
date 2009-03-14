
import pygame

from inkface.altsvg.element import Element

from inkface.canvas import Face
from inkface.canvas import CanvasElement


v_major, v_minor, _ = pygame.version.vernum

if v_major <= 1 and v_minor < 8:
    USE_DIRTY = False
else:
    USE_DIRTY = True

num_module = None
try:
    import numpy
    num_module = 'numpy'
except ImportError, ie:
    try:
        import Numeric
        num_module = 'Numeric'
    except ImportError, ie:
        pass
        
from copy import copy

def ARGB2RGBA_numpy(surface):
    buf = surface.get_data()
    a = numpy.frombuffer(buf,numpy.uint8)
    a.shape = (surface.get_width(),
                surface.get_height(),4)
    tmp = copy(a[:,:,0])
    a[:,:,0] = a[:,:,2]
    a[:,:,2] = tmp
    return a

def ARGB2RGBA_Numeric(surface):
    buf = surface.get_data()
    a = Numeric.fromstring(buf,Numeric.UInt8)
    a.shape = (surface.get_width(),
                surface.get_height(),4)
    tmp = copy(a[:,:,0])
    a[:,:,0] = a[:,:,2]
    a[:,:,2] = tmp
    return a


def ARGB2RGBA_python(surface):
    # cairo's ARGB is interpreted by pygame as BGRA due to 
    # then endian-format difference this routine swaps B and R 
    # (0th and 2nd) byte converting it to RGBA format.
    buf = surface.get_data()
    import array
    byte_buf = array.array("c", buf)
    num_quads = len(byte_buf)/4
    for i in xrange(num_quads):
        tmp = byte_buf[i*4 + 0]
        byte_buf[i*4 + 0] = byte_buf[i*4 + 2]
        byte_buf[i*4 + 2] = tmp
    return byte_buf


if num_module == 'numpy':
    ARGB2RGBA = ARGB2RGBA_numpy
elif num_module == 'Numeric':
    ARGB2RGBA = ARGB2RGBA_Numeric
else:
    ARGB2RGBA = ARGB2RGBA_python
    
class PygameFace(Face):

    # TODO /face dup code
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
    # TODO /face dup code

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

    if USE_DIRTY:
        class ElementSprite(pygame.sprite.DirtySprite):
            def __init__(self,parent):
                pygame.sprite.DirtySprite.__init__(self)
                self.parent = parent

            def update(self,*args):
                if self.parent.onDraw != None:
                    self.parent.onDraw(self.parent)

    else:
        class ElementSprite(pygame.sprite.Sprite):
            def __init__(self,parent):
                pygame.sprite.Sprite.__init__(self)
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
        

    '''
        Implementation of hide/unhide without using "Dirty" sprites and groups.

        Pygame 1.8.0 introduced DirtySprites which have attributes like 
        "visible" and "dirty", which are read by LayeredDirty group while
        drawing the sprites. So we use them directly to hide or unhide sprites

        For versions <1.8.0, we can't use this straightforward method. 
        In older version, we set and use the "visible" attribute ourselves.
        For hiding an element we simply remove it from the group sprite.kill()
        For unhiding, we mark the visible flag to 1 and mark one more flag
        "visibility_changed"

        In canvas's paint() function, the canvas checks if any element's 
        visibility has changed. If so, it clears the group and reforms it 
        with elements that are visible at that point.

        The reason for the asymmetry in logic is: sprite removal and addition
        API for group is also asymmetric. Sprite doesn't need to know about
        groups it belongs to to remove it from them. But to add it to group
        it needs a reference to the group, which it doesn't have. So canvas has
        to do that when indicated so by visibility_changed flag.
    '''
    def hide(self):
        '''
            Marks the element sprite invisible and dirty.
            Warning: You may still see the element after calling hide() if
            you have overridden the onDraw callback and calling unhide() there 
        '''
        if self.sprite.visible == 1:   
            self.sprite.visible = 0
            self.sprite.dirty = 1

        if not USE_DIRTY:
            self.sprite.kill()

    def unhide(self):
        if self.sprite.visible == 0:
            self.sprite.visible = 1
            self.sprite.dirty = 1

        if not USE_DIRTY:
            self.sprite.visibility_changed = True
        
    def __init__(self,svgelem):
        CanvasElement.__init__(self,svgelem)
        self.sprite = self.ElementSprite(self)
        self.sprite.visible = 1
        self.sprite.dirty = 1
        if not USE_DIRTY:
            self.sprite.visibility_changed = True
        self.surface_converted = False
        self.refresh()

    def refresh(self,svg_reload=False):
        if svg_reload or self.svg.surface == None:
            self.svg.render()
            self.surface_converted = False

        if not self.surface_converted:
            self.buf = ARGB2RGBA(self.svg.surface)
            self.surface_converted = True

        image = pygame.image.frombuffer(self.buf.tostring(),
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

        if USE_DIRTY:
            self.elem_group = pygame.sprite.LayeredDirty(
                _use_update=True, _time_threshold=1000./framerate)
        else:
            self.elem_group = pygame.sprite.OrderedUpdates()

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

        if not USE_DIRTY:
            needs_refresh = False
            for elem in self.elementQ:
                if elem.sprite.visibility_changed:
                    needs_refresh = True
                    break
            if needs_refresh:
                self.elem_group.empty()
                for elem in self.elementQ:
                    elem.sprite.visibility_changed = False
                    if elem.sprite.visible == 1:
                        self.elem_group.add(elem.sprite)


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

       
 
