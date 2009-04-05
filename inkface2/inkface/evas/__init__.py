
import os
import cairo

import ecore.evas

from inkface.altsvg.element import Element
from inkface.canvas import Canvas, Face, CanvasElement


class EFace(Face):
    def __init__(self, svgname, canvas=None):
        Face.__init__(self, svgname)
        if canvas is not None:
            self.load_elements(canvas)

    def load_elements(self, canvas):
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

        svge = self.get(newNodeName).svg
        ecElement = ECanvasElement(svge, self.canvas)

        Face._append(self, svge, ecElement)



class ECanvasElement(CanvasElement):
    def __init__(self, svgelem, canvas):
        CanvasElement.__init__(self, svgelem)

        self.canvas = canvas

        if self.svg.surface is None:
            self.svg.render()

        surface = self.svg.surface

        w, h = surface.get_width(), surface.get_height()
        self.image = self.canvas.canvas.Image()
        self.image.alpha_set(True)
        self.image.image_size_set(w, h)
        self.image.fill_set(0, 0, w, h)
        self.image.image_data_set(surface.get_data())
        self.image.resize(w, h)
        x, y = self.get_position()
        self.image.move(x, y)
        self.image.show()

    def refresh(self):
        self.svg.render()
        surface = self.svg.surface
        w, h = surface.get_width(), surface.get_height()
        self.image = self.canvas.canvas.Image()
        self.image.alpha_set(True)
        self.image.image_size_set(w, h)
        self.image.fill_set(0, 0, w, h)
        self.image.image_data_set(surface.get_data())
        self.image.resize(w, h)
        self.image.show()

    def hide(self):
        self.image.hide()

    def unhide(self):
        self.image.show()

    def dup(self, newName):
        new_svg = self.svg.dup(newName)
        return ECanvasElement(new_svg, self.canvas)

class ECanvas(Canvas):
    def __init__(self,
                (width,height) = (640, 480),
                caption = 'Evas Inkface App',
                framerate = 60.0):

        Canvas.__init__(self)

        self.ee = ecore.evas.SoftwareX11(w=width, h=height)
        self.ee.title = caption
        self.canvas = self.ee.evas
        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            self.ee.fullscreen = True


    def add(self, face):
        #Canvas.add(self, face)
        print 'ECanvas::add not needed'

    def eventloop(self):
        self.ee.show()
        ecore.main_loop_begin()
