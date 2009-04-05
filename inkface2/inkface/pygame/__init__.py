'''

module:: inkface.canvas.pygamecanvas -- Pygame Canvas Backend
=============================================================

:synopsis: This module contains Class definitions used for Pygame Canvas Backend
'''
import os
import pygame

from inkface.altsvg.element import Element

from inkface.canvas import Face, Canvas, CanvasElement


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
    '''
    Loads SVG file and creates PygameCanvasElement object from it.
    These objects can be accessed as members of this Face instance,
    addressed by the *label* given to them in Image editor.
    '''
    def __init__(self,svgname):
        Face.__init__(self,svgname)

        for svge in self.svgelements:
            pcElement = PygameCanvasElement(svge)
            Face._append(self, svge, pcElement)

    def clone(self, curNodeName, newNodeName, new_x=-1, new_y=-1):
        '''
        Clones an existing element of the face to create a duplicate one.

        :param curNodeName: name of existing element to be cloned
        :param newNodeName: name the new element should have
        :param new_x: [optional] x coord of new element
        :param new_y: [optional] y coord of new element
        '''
        Face.clone(self, curNodeName, newNodeName, new_x, new_y)

        if self.parent_canvas is not None:
            self.parent_canvas.insert_after(
                self.get(curNodeName), self.get(newNodeName))


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
        Hides this element.
        Warning: There is a difference in semantics of this call, depending on
        the pygame version.

        * For pygame version < 1.8.x - Calling hide() will disable the call to
          onDraw handler of it too. The onDraw of this element won't be called
          until unhide() is called. 
        * For pygame version >= 1.8.x - Calling hide() won't disable the call 
          onDraw handler of this element. The onDraw handler will still be
          called during each refresh cycle. You can use it to unhide this
          element.

        '''
        if self.sprite.visible == 1:   
            self.sprite.visible = 0
            self.sprite.dirty = 1

        if not USE_DIRTY:
            self.sprite.kill()

    def unhide(self):
        '''
        Unhides this element
        '''
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

    def refresh(self, svg_reload=False, sprite_reload=True):
        '''
        Redraws the SVG element's cairo surface on PygameCanvasElement's
        sprite.

        :param svg_reload: If underlying SVG should be redrawn. \
        This needs to be true if you have made changes to the SVG \
        node and need the change to reflect on screen
        :param sprite_reload: If sprite should be reloaded. \
        There are cases when SVG is changed and reloaded, but only \
        for purposes of getting estimate of final dimensions. \
        In such case the change is not to be reflected on screen. \
        By setting this param to True, one can save time spent in \
        reloading the sprite. This is only for performance \
        improvement purposes. Even if the sprite gets reloaded, the \
        change won't get reflected until the canvas gets redrawn.
        '''
        if svg_reload or self.svg.surface == None:
            self.svg.render()
            self.surface_converted = False

        if not sprite_reload: return

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

        new_svg = self.svg.dup(newName)
        return PygameCanvasElement(new_svg)

import threading

class PygameCanvas(Canvas):
    '''
    :param resolution: Dimensions of the canvas
    :param caption: Caption of the application window (if supported by platform)
    :param framerate: Rate at which to refresh the canvas \
    (frames per second - fps). The canvas spawns an internal thread to do \
    this periodic refresh. If you are not interested in animation in GUI, \
    then you can mention framerate=0 and the extra thread won't be spawned. \
    In such situation, you will have to manually call paint() method of \
    canvas if you want the canvas to be refreshed.
    :param flags: You can pass additional pygame flags that will be passed \
    to pygame.display.set_mode() call.
    '''
    def __init__(self,
                resolution  = (640,480),
                caption     = 'Inkface App',
                framerate   = 25,
                flags       = 0):

        Canvas.__init__(self)

        resolution = map(lambda x: int(x), resolution)

        # Check for fullscreen hint from environment
        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = flags | pygame.FULLSCREEN

        pygame.init()
        self.screen = pygame.display.set_mode(
                        resolution, pygame.DOUBLEBUF|flags)
        self.dispsurf = pygame.Surface(self.screen.get_size())
        self.dispsurf.convert()
        pygame.display.set_caption(caption)

        if USE_DIRTY:
            if framerate > 0:
                self.elem_group = pygame.sprite.LayeredDirty(
                    _use_update=True, _time_threshold=1000./framerate)
            else:
                self.elem_group = pygame.sprite.LayeredDirty(
                    _use_update=True)
        else:
            self.elem_group = pygame.sprite.OrderedUpdates()

        self.framerate = framerate
        if self.framerate > 0:
            self.clock = pygame.time.Clock()
            self.painter = self._PainterThread(self)
            self.painter.start()

        self.stop_signal = False

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
        '''
        Redraws the canvas
        '''
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

    def insert_after(self, existing_elem, new_elem):
        Canvas.insert_after(self, existing_elem, new_elem)
        self.elem_group.empty()
        for elem in self.elementQ:
            self.elem_group.add(elem.sprite)

    def add(self,face):
        '''
        :param face: PygameFace instance to add to this canvas. \
        This actually leads to addition of Face's elements to canvas's \
        current list of elements.
        '''
        Canvas.add(self, face)
        face.parent_canvas = self
        for elem in self.elementQ:
            self.elem_group.add(elem.sprite)

    def remove(self, face):
        '''
        :param face: PygameFace instance to remove from this canvas. \
        This actually leads to removal of Face's elements from canvas's \
        current list of elements.
        '''
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
        '''
        Cleans up the canvas (and its internal thread, if applicable).
        '''
        self.stop_signal = True
        try:
            if self.painter != None:
                self.painter.stop()
                self.painter.join()
        except AttributeError, ae:
            # In case there is no painter thread
            pass

    def eventloop(self):
        '''
        The loop that application should call after it has setup all GUI \
        elements and is ready to handle events from user.
        '''
        while True:
            self._handle_event(pygame.event.wait())

            if self.stop_signal: 
                return

       
 
