
import inkface
import inklib
import re

KEYBOARD_SVG='keyboard.svg'

class Keyboard(inklib.Face):
    visible = False
    glowing_elements = {}
    def __init__(self,canvas):
        inklib.Face.__init__(self,canvas,KEYBOARD_SVG)

        for k,e in self.elements.items():
            if e.name.startswith('key'):
                if e.name.endswith('Glow'):
                    e.opacity = 0
                    e.onDraw = self.glowDraw
                    self.glowing_elements[e.name] = 0
                else:
                    e.onTap = self.onAlNumTap

        self.keySpace.onTap = self.onSpace
        self.keyEnter.onTap = self.onEnter

        self.keyboardText.text = ''
        self.keyboardText.refresh()

        self.canvas.onTimer = self.onTimer
        self.canvas.timeout = 100

    def onTimer(self):
        for k,v in self.glowing_elements.items():
            if v > 0:
                self.glowing_elements[k] = v - 1
            elif v == 0:
                self.elements[k].opacity = 0
                self.canvas.refresh()

    def onSpace(self,e):
        self.keyboardText.text += ' '
        self.keyboardText.refresh()

    def onAlNumTap(self,e):
        m = re.match('key(\w)',e.name)
        letter = m.group(1)
        self.keyboardText.text += letter
        self.keyboardText.refresh()
        try:
            ge = self.elements[e.name+'Glow']
            if ge: 
                ge.opacity = 1
                self.glowing_elements[ge.name] = 3
        except KeyError,ke:
            pass
        self.canvas.refresh()

    def onEnter(self,e):
        self.canvas.remove(self)
        self.canvas.refresh()
        
    def glowDraw(self,e):
        if e.opacity:
            self.canvas.draw(e)

    def onKeyPress(self,txt,code,elements):
        pass



