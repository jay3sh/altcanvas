'''
    The caps lock keys don't work for pygame right now.
    PygameCanvasElement is not programmed to ignore click events if
    it is hidden state. That will be fixed in future.
    The rest of functionality of keyboard and textbox widgets is working.
'''
import sys

from inkface.pygame import PygameFace, PygameCanvas

from inkface.widgets.keyboard import Keyboard
from inkface.widgets.textbox import Textbox


class App:
    def __init__(self):
        pass

    def main(self, txtb_svg, kbd_svg):
        txtb_face = PygameFace(txtb_svg)
        kbd_face = PygameFace(kbd_svg)

        self.canvas = PygameCanvas((800,480),framerate=25)

        self.kbd = Keyboard(kbd_face)

        self.textbox = Textbox(
                        border_elem = txtb_face.border,
                        txt_elem    = txtb_face.txt,
                        cursor_elem = txtb_face.cursor,
                        focus_elem  = txtb_face.borderfocus,
                        kbd         = self.kbd)

                    
        self.canvas.add(txtb_face)
        self.canvas.add(kbd_face)

        self.kbd.hide()
        self.canvas.paint()

        self.canvas.eventloop()

if __name__ == '__main__':
    App().main(sys.argv[1], sys.argv[2])


