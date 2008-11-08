#!/usr/bin/env python

import os
import sys
import inkface

canvas = None
textbox = None
KEYBOARD_SVG=sys.argv[1]

special_key_map = {
    'Period':'.',
    'Comma':',',
    'SemiColon':';',
    'Question':'?',
    'Exclaim':'!',
    'At':'@',
    'Pound':'#',
    'Percent':'%',
    'Star':'*',
    'DQuote':'"',
    'LPara':'(',
    'RPara':')',
    'Amp':'&'
    }

def onSpacebar(e,elements):
    global canvas
    textbox.text = textbox.text+' '
    textbox.refresh()
    canvas.refresh()

def onBackspace(e,elements):
    global canvas
    textbox.text = textbox.text[:-1]
    textbox.refresh()
    canvas.refresh()

def onEnter(e,elements):
    global canvas
    for el in elements:
        if el.name.startswith('msgbox'):
            el.opacity = 1
            if el.name == 'msgboxText':
                el.text = textbox.text[:25]+'\n'+textbox.text[25:]
                el.refresh()
    textbox.text = ''
    textbox.refresh()
    canvas.refresh()

def onSpecialKey(e,elements):
    global canvas
    textbox.text = textbox.text + special_key_map[e.name[5:]]
    textbox.refresh()
    canvas.refresh()

def onKeyEnter(e,elements):
    global canvas
    for el in elements:
        if el.name == e.name+'Glow':
            el.opacity = 1
    textbox.text = textbox.text+e.name[3]
    textbox.refresh()
    canvas.refresh()

def onKeyLeave(e,elements):
    for el in elements:
        if el.name == e.name+'Glow':
            el.opacity = 0
    canvas.refresh()

def onKeyGlowDraw(e):
    global canvas
    if e.opacity:
        canvas.draw(e)

def onExit(e,elements):
    inkface.exit()
    sys.exit(0)

def onMsgBoxDraw(e):
    global canvas
    if e.opacity:
        canvas.draw(e)

def onMsgBoxOK(e,elist):
    global canvas
    for el in elist:
        if el.name.startswith('msgbox'):
            el.opacity = 0
    canvas.refresh()

def onKeyboardKeyPressed(e,string,keycode,elements):
    global canvas
    textbox.text = textbox.text+string.strip()

    if keycode == inkface.KeyEscape:
        onExit(e,elements)
    elif keycode == inkface.KeyBackspace:
        onBackspace(e,elements)
    elif keycode == inkface.KeyEnter:
        onEnter(e,elements) 
    elif keycode == inkface.KeySpace:
        textbox.text = textbox.text + ' '

    textbox.refresh()
    canvas.refresh()

   
def main():
    global canvas
    global textbox
    elements = inkface.loadsvg(KEYBOARD_SVG)
    canvas = inkface.create_X_canvas()
    canvas.register_elements(elements)

    # Wire handlers and init some elements
    for e in elements:
        if e.name == 'keySpace':
            #e.onMouseEnter = onSpacebar
            e.onTap = onSpacebar
        elif e.name == 'keyEnter':
            #e.onMouseEnter = onEnter
            e.onTap = onEnter
        elif e.name == 'keyBackspace':
            #e.onMouseEnter = onBackspace
            e.onTap = onBackspace
        elif e.name.startswith('keySp'):
            #e.onMouseEnter = onSpecialKey
            e.onTap = onSpecialKey
        elif e.name.startswith('key'):
            if e.name.endswith('Glow'):
                e.opacity = 0
                e.onDraw = onKeyGlowDraw
            else:
                #e.onMouseEnter = onKeyEnter
                e.onTap = onKeyEnter
                e.onMouseLeave = onKeyLeave
                e.opacity = 1
        elif e.name == 'exitDoor':
            #e.onMouseEnter = onExit
            e.onTap = onExit
        elif e.name == 'textBox':
            textbox = e
            textbox.text = ''
            textbox.onKeyPress = onKeyboardKeyPressed
            textbox.refresh()
        elif e.name.startswith('msgbox'):
            e.opacity = 0
            e.onDraw = onMsgBoxDraw
            if e.name == 'msgboxOK':
                e.onMouseEnter = onMsgBoxOK

    # eventloop
    canvas.eventloop()

if __name__ == '__main__':
    main()
