#!/usr/bin/env python

import inkface

NOTEPAD_SVG='notepad.svg'
canvas = None

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

    canvas.eventloop()

if __name__ == '__main__':
    main()
