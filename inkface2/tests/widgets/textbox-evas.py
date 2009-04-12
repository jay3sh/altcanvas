import sys

from inkface.evas import EFace, ECanvas

from inkface.widgets.keyboard import Keyboard
from inkface.widgets.textbox import Textbox


class App:
    def __init__(self):
        pass

    def main(self, txtb_svg, kbd_svg):
        self.canvas = ECanvas((800,480),framerate=25)

        txtb_face = EFace(txtb_svg, self.canvas)
        kbd_face = EFace(kbd_svg, self.canvas)

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

        self.canvas.eventloop()

if __name__ == '__main__':
    App().main(sys.argv[1], sys.argv[2])


