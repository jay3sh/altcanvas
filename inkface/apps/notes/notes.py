#!/usr/bin/env python

import inkface
from keyboard import Keyboard

NOTEPAD_SVG='notepad.svg'

class Notepad:
    kbd = None
    def __init__(self):
        self.canvas = inkface.create_X_canvas()
        self.elements = inkface.loadsvg(NOTEPAD_SVG)
        self.canvas.register_elements(self.elements)
        for e in self.elements:
            if e.name == 'note':
                e.text = ''
                e.onKeyPress = self.onKeyPress
                e.refresh()
                self.note = e
            elif e.name == 'keyKeyboard':
                e.onTap = self.launchKeyboard

    def launchKeyboard(self,e,elements):
        if not self.kbd:
            self.kbd = Keyboard(self.canvas)
            self.canvas.register_elements(self.kbd.elements)
        self.kbd.visible = True
        self.canvas.refresh()
 
    def onKeyPress(self,note,txt,code,elements):
        self.note.text = note.text + txt

        if code == inkface.KeyBackspace:
            note.text = note.text[:-1]
        elif code == inkface.KeyEscape:
            inkface.exit()

        self.note.refresh()
        self.canvas.refresh()

    def run(self):
        self.canvas.eventloop()

def main():
    notepad = Notepad()
    notepad.run()

if __name__ == '__main__':
    main()
