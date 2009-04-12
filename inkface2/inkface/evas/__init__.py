
import os
import cairo

import ecore.evas
import evas

from inkface.altsvg.element import Element
from inkface.canvas import Canvas, Face, CanvasElement


class EFace(Face):
    '''
    Evas Face object.

    :param svgname: Path of the SVG file to load
    :param canvas: Optional argument. If it is not passed, the elements \
    won't be loaded. In that case call :func:`load_elements` with the \
    canvas argument. This is because of the nature of Evas canvas. Since \
    it keeps the state of all elements drawn on it, they have to be \
    created from it, so that it knows about them.
    '''

    def __init__(self, svgname, canvas=None):
        Face.__init__(self, svgname)
        if canvas is not None:
            self.load_elements(canvas)

    def load_elements(self, canvas):
        '''
        Loads elements of this face.

        :param canvas: Canvas to create elements from.
        '''
        self.canvas = canvas
        for svge in self.svgelements:
            ecElement = ECanvasElement(svge, canvas)
            Face._append(self, svge, ecElement)

    def clone(self, curNodeName, newNodeName, new_x=-1, new_y=-1):
        '''
        Clones an existing element of the face to create a duplicate one.

        :param curNodeName: name of existing element to be cloned
        :param newNodeName: name the new element should have
        :param new_x: [optional] x coord of new element
        :param new_y: [optional] y coord of new element
        '''
        Face.clone(self, curNodeName, newNodeName, new_x, new_y)


class ECanvasElement(CanvasElement):
    '''
    Evas CanvasElement object.

    :param svgelem: :class:`inkface.altsvg.element.Element` object 
    :param canvas: Canvas to create this element from.
    '''
    def __init__(self, svgelem, canvas):
        CanvasElement.__init__(self, svgelem)

        self.canvas = canvas

        self.image = None

        if self.svg.surface is None:
            self.refresh(svg_reload = True)
        else:
            self.refresh(svg_reload = False)

    def set_position(self, (x, y)):
        '''
        :param (x,y): x,y coordinates to set this element's position to
        '''
        CanvasElement.set_position(self, (x, y))
        x, y = self.get_position()
        self.image.move(x, y)

    def refresh(self, svg_reload=True, imgpath=None):
        '''
        Refresh the element.

        :param svg_reload: re-render the SVG underlying element \
        (default - True)
        :param imgpath: Instead of rendering the SVG element, load an image \
        and render it on this element. It is useful in scenarios, where \
        the SVG element is used only to get the location. Its content are \
        dynamically filled by the app at run time.
        '''
        if svg_reload:
            self.svg.render()
        surface = self.svg.surface
        w, h = surface.get_width(), surface.get_height()
        if self.image is not None:
            self.image.delete()

        if imgpath is None:
            self.image = self.canvas.canvas.Image()
            self.image.alpha_set(True)
            self.image.image_size_set(w, h)
            self.image.fill_set(0, 0, w, h)
            self.image.image_data_set(surface.get_data())
            self.image.resize(w, h)
        else:
            x, y = self.get_position()
            self.image = self.canvas.canvas.Image(file=imgpath)
            self.image.size = (w, h)
            self.image.fill = (0, 0, w, h)

        # wire the new image with event handlers
        self.image.event_callback_add(
            evas.EVAS_CALLBACK_MOUSE_DOWN, self._handle_mouse_down)
        self.image.event_callback_add(
            evas.EVAS_CALLBACK_MOUSE_IN, self._handle_mouse_entry)
        self.image.event_callback_add(
            evas.EVAS_CALLBACK_MOUSE_OUT, self._handle_mouse_entry)

        x, y = self.get_position()
        self.image.move(x, y)
        self.image.show()

    def hide(self):
        '''
        Hide this element
        '''
        self.image.hide()

    def __setattr__(self, key, value):
        if key == 'onDraw':
            if value is not None:
                if self.__dict__.has_key('onDrawAnimator'):
                    self.__dict__['onDrawAnimator'].stop()
                    self.__dict__['onDrawAnimator'].delete()
                animator = ecore.animator_add(value, self)
                self.__dict__['onDrawAnimator'] = animator
        else:
            self.__dict__[key] = value


    def _handle_mouse_down(self, image, event, *args):
        mouse_button_handlers = \
            {   
                1:self.onLeftClick,
                2:self.onMiddleClick,
                3:self.onRightClick
            }
        handler = mouse_button_handlers[event.button]
        if handler is not None:
            handler(self)

    def _handle_mouse_entry(self, image, event, *args):
        if type(event) == evas.c_evas.EventMouseIn:
            if self.onMouseGainFocus is not None:
                self.onMouseGainFocus(self)
        elif type(event) == evas.c_evas.EventMouseOut:
            if self.onMouseLoseFocus is not None:
                self.onMouseLoseFocus(self)

    def unhide(self):
        '''
        Unhide this element.
        '''
        self.image.show()

    def dup(self, newName):
        '''
        Create duplicate copy of this element.
        '''
        new_svg = self.svg.dup(newName)
        return ECanvasElement(new_svg, self.canvas)

    def destroy(self):
        try:
            if self.onDrawAnimator is not None:
                self.onDrawAnimator.stop()
                self.onDrawAnimator.delete()
        except AttributeError, ae:
            pass

        self.image.delete()
        del self.image

class ECanvas(Canvas):
    '''
    Evas Canvas object.

    :param (width, height): dimensions of canvas
    :param caption: Title of window
    :param framerate: Animation framerate (in fps)
    '''
    def __init__(self,
                (width,height) = (640, 480),
                caption = 'Evas Inkface App',
                framerate = 0):

        Canvas.__init__(self)

        self.framerate = framerate

        self.ee = ecore.evas.SoftwareX11(w=width, h=height)
        self.ee.title = caption
        self.canvas = self.ee.evas
        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            self.ee.fullscreen = True

    def refresh(self):
        ecore.main_loop_iterate()

    def add(self, face):
        '''
        This is a no-op so far for Evas Canvas.
        '''
        #Canvas.add(self, face)
        pass

    def remove(self, face):
        '''
        Remove all elements of the face from canvas
        :param face: Face of whose elements are to be removed from canvas.
        '''
        for elem in face.elements:
            elem.destroy()
        
    def stop(self):
        '''
        Call to cleanup the canvas when exiting.
        '''
        ecore.main_loop_quit()
        ecore.shutdown()

    def eventloop(self):
        '''
        It calls ecore.main_loop_begin.
        If framerate is >0, then it sets the animator_frametime.
        '''
        self.ee.show()
        if self.framerate != 0:
            ecore.animator_frametime_set(1.0/float(self.framerate))
        ecore.main_loop_begin()
