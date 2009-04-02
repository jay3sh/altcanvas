
import cairo

import ecore.evas

from inkface.altsvg.element import Element
from inkface.canvas.canvas import Canvas
from inkface.canvas import Face
from inkface.canvas import CanvasElement


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


class ECanvasElement(CanvasElement):
    def __init__(self, svgelem, canvas):
        CanvasElement.__init__(self, svgelem)

        if self.svg.surface is None:
            self.svg.render()

        surface = self.svg.surface

        w, h = surface.get_width(), surface.get_height()
        self.canvas = canvas.canvas
        self.image = self.canvas.Image()
        self.image.alpha_set(True)
        self.image.image_size_set(w, h)
        self.image.fill_set(0, 0, w, h)
        self.image.image_data_set(surface.get_data())
        self.image.resize(w, h)
        self.image.show()


class ECanvas(Canvas):
    def __init__(self,
                (width,height) = (640, 480),
                caption = 'Evas Inkface App'):

        Canvas.__init__(self)

        self.ee = ecore.evas.SoftwareX11(w=width, h=height)
        self.canvas = self.ee.evas

    def add(self, face):
        Canvas.add(self, face)

    def eventloop(self):
        self.ee.show()
        ecore.main_loop_begin()
