
import cairo
import clutter
import cluttercairo

from inkface.altsvg.element import Element
from inkface.canvas.canvas import Canvas
from inkface.canvas import Face
from inkface.canvas import CanvasElement

class ClutterFace(Face):
    def __init__(self,svgname):
        Face.__init__(self,svgname)

        for svge in self.svgelements:
            ccElement = ClutterCanvasElement(svge)
            Face._append(self, svge, ccElement)


class ClutterCanvasElement(CanvasElement):

    def __init__(self, svgelem):
        CanvasElement.__init__(self, svgelem)

        self.actor = cluttercairo.CairoTexture(
                            width = svgelem.w,
                            height = svgelem.h)
    
        self.actor.set_position(
                            x = int(svgelem.x),
                            y = int(svgelem.y))

        self.refresh(svg_reload=False)

    def hide(self):
        pass

    def unhide(self):
        pass

    def refresh(self, svg_reload=True):
        if svg_reload or self.svg.surface is None:
            self.svg.render()

        ctx = self.actor.cairo_create()

        ctx.set_operator(cairo.OPERATOR_CLEAR)
        ctx.paint()

        ctx.set_operator(cairo.OPERATOR_OVER)
        ctx.set_source_surface(self.svg.surface)
        ctx.paint()
        del(ctx)
        
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
        pass

    def _on_mouse_motion(self, stage, event):
        pass

    def _on_button_press(self, stage, event):
        for elem in self.elementQ:
            if elem.occupies((event.x, event.y)) and \
                not elem.clouded((event.x, event.y)):

                if event.button == 1 and \
                    elem.onLeftClick is not None:

                    elem.onLeftClick(elem)

                elif event.button == 3 and \
                    elem.onRightClick is not None:

                    elem.onRightClick(elem)
            
        
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
