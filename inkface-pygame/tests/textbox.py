from inkface.canvas import PygameFace, PygameCanvas
import sys

class App:
    FLASH_COUNT = 10
    dir = 1
    def main(self):
        try:
            self.canvas = PygameCanvas((800,480))
            self.face = PygameFace('data/gui-14.svg')

            self.face.cursor.onDraw = self.onCursorDraw
            self.face.cursor.flash_counter = 0

            self.face.txt.onKeyPress = self.onKeyPress

            self.face.txt.svg.text = "_"
            self.face.txt.text = self.face.txt.svg.text
            self.face.txt.refresh(svg_reload=True)

            self.canvas.add(self.face)
            self.canvas.eventloop()
        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.canvas.stop()
            sys.exit(0)

    def onCursorDraw(self, elem):
        txt_x, txt_y = self.face.txt.get_position()
        elem_x = txt_x + self.face.txt.svg.w + 2
        elem_y = txt_y
        elem.set_position((elem_x,elem_y))

        if abs(elem.flash_counter) >= self.FLASH_COUNT:
            if self.dir > 0:
                elem.hide()
            else:
                elem.unhide()
            self.dir = -1 * self.dir

        elem.flash_counter += self.dir
        
    def onKeyPress(self, elem, event):
        elem.text += event.unicode
        elem.svg.text += event.unicode
        elem.refresh(svg_reload=True)

        elem_x, elem_y = elem.get_position()
        textbox_x, textbox_y = self.face.textbox.get_position()
        elem_x_offset = elem_x - textbox_x
        textbox_width = self.face.textbox.svg.w - self.face.cursor.svg.w - elem_x_offset
        while (elem_x_offset + elem.svg.w) > textbox_width:
            elem.svg.text = elem.svg.text[1:]
            elem.refresh(svg_reload=True)

        self.canvas.update()

App().main()
