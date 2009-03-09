from inkface.canvas import PygameFace, PygameCanvas
import sys


class TextBox:
    FLASH_COUNT = 10
    counter_dir = 1
    def __init__(self, border_elem, txt_elem, cursor_elem):
        self.border_elem = border_elem
        self.txt_elem = txt_elem
        self.cursor_elem = cursor_elem

        self.cursor_elem.onDraw = self._onCursorDraw
        self.cursor_elem.flash_counter = 0

        self.txt_elem.onKeyPress = self._onKeyPress
        self.txt_elem.svg.text = "_"
        self.txt_elem.text = self.txt_elem.svg.text
        self.txt_elem.refresh(svg_reload=True)

    def _onKeyPress(self, elem, event):
        elem.text += event.unicode
        elem.svg.text += event.unicode
        elem.refresh(svg_reload=True)

        elem_x, elem_y = elem.get_position()
        textbox_x, textbox_y = self.border_elem.get_position()
        elem_x_offset = elem_x - textbox_x
        textbox_width = self.border_elem.svg.w - self.cursor_elem.svg.w - elem_x_offset
        while (elem_x_offset + elem.svg.w) > textbox_width:
            elem.svg.text = elem.svg.text[1:]
            elem.refresh(svg_reload=True)

    def _onCursorDraw(self, elem):
        txt_x, txt_y = self.txt_elem.get_position()
        elem_x = txt_x + self.txt_elem.svg.w + 2
        elem_y = txt_y
        elem.set_position((elem_x,elem_y))

        if abs(elem.flash_counter) >= self.FLASH_COUNT:
            if self.counter_dir > 0:
                elem.hide()
            else:
                elem.unhide()
            self.counter_dir = -1 * self.counter_dir

        elem.flash_counter += self.counter_dir
 
        
class App:
    FLASH_COUNT = 10
    dir = 1
    def main(self):
        try:
            self.canvas = PygameCanvas((800,480))
            self.face = PygameFace('data/gui-14.svg')

            tb = TextBox(border_elem=self.face.border,
                        txt_elem=self.face.txt,
                        cursor_elem=self.face.cursor)

            self.canvas.add(self.face)
            self.canvas.eventloop()
        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.canvas.stop()
            sys.exit(0)

App().main()