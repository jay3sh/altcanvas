
import clutter
import cluttercairo

from inkface.altsvg.element import Element
from inkface.canvas.canvas import Canvas
from inkface.canvas import Face
from inkface.canvas import CanvasElement

class ClutterFace(Face):
    # TODO face dup code
    def __init__(self,svgname):
        Face.__init__(self,svgname)

        self.elements = []
        self._elements_dict = {}

        for svge in self.svgelements:
            pElement = ClutterCanvasElement(svge)
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



class ClutterCanvasElement(CanvasElement):

    def __init__(self, svgelem):
        CanvasElement.__init__(self, svgelem)

        self.actor = cluttercairo.CairoTexture(
                            width = svgelem.w,
                            height = svgelem.h)
    
        self.actor.set_position(
                            x = svgelem.x,
                            y = svgelem.y)

        ctx = self.actor.cairo_create()
        ctx.set_source_surface(svgelem.surface)
        ctx.paint()

    def hide(self):
        pass

    def unhide(self):
        pass

class ClutterCanvas(Canvas):
    def __init__(self,
                (width,height) = (640, 480),
                caption = 'Clutter Inkface App'):
        Canvas.__init__(self)

        self.stage = clutter.Stage()
        self.stage.set_size(width=width,height=height)
        
        self.stage.connect('key-press-event',self._on_key_press)
        self.stage.connect('motion-event',self._on_mouse_motion)
        self.stage.connect('button-press-event',self._on_button_press)

        self.stage.connect('destroy', clutter.main_quit)

    def _on_key_press(self, stage, event):
        print 'key pressed'

    def _on_mouse_motion(self, stage, event):
        print 'mouse moved'

    def _on_button_press(self, stage, event):
        print 'button pressed'
        
    def add(self, face):
        Canvas.add(self, face)
        for elem in self.elementQ:
            self.stage.add(elem.actor)

    def remove(self, face):
        pass

    def stop(self):
        clutter.main_quit()

    def eventloop(self):
        self.stage.show_all()
        clutter.main()
