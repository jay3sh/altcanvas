#!/usr/bin/env python

import inkface

NOTEPAD_SVG='notepad.svg'
KEYBOARD_SVG='keyboard-black.svg'
canvas = None


class Keyboard:
    def __init__(self,canvas):
        self.canvas = canvas
        self.elements = inkface.loadsvg(KEYBOARD_SVG)
        for e in self.elements:
            if e.name.startswith('key'):
                e.onTap = self.onTap
            elif e.name.endswith('Glow'):
                e.opacity = 0
                e.onDraw = self.glowDraw

    def onTap(self,e,elements):
        pass
        
    def glowDraw(self,e):
        print 'glowDrawing'
        if e.opacity:
            self.canvas.draw(e)

    def onKeyPress(self,txt,code,elements):
        print txt


def onKeyPress(note,txt,code,elements):
    global canvas
    note.text = note.text + txt

    if code == inkface.KeyBackspace:
        note.text = note.text[:-1]
    elif code == inkface.KeyEscape:
        inkface.exit()

    note.refresh()
    canvas.refresh()

def main():
    global canvas
    elements = inkface.loadsvg(NOTEPAD_SVG)
    canvas = inkface.create_X_canvas()
    canvas.register_elements(elements)

    for e in elements:
        if e.name == 'note':
            e.text = ''
            e.onKeyPress = onKeyPress
            e.refresh()

    # Temp
    kbd = Keyboard(canvas)
    canvas.register_elements(kbd.elements)
    # /Temp

    canvas.eventloop()

if __name__ == '__main__':
    main()
