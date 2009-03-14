
import clutter
import cluttercairo

from inkface.altsvg.element import Element
from inkface.canvas.canvas import Canvas
from inkface.canvas import Face
from inkface.canvas import CanvasElement

class ClutterFace(Face):
    pass


class ClutterCanvasElement(CanvasElement):
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
        
    def stop(self):
        clutter.main_quit()

    def eventloop(self):
        self.stage.show_all()
        clutter.main()
