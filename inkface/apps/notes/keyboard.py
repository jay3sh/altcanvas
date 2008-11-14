
import inkface

KEYBOARD_SVG='keyboard.svg'

class Keyboard:
    visible = False
    elements_dict = {}
    glowing_elements = {}
    def __init__(self,canvas):
        self.canvas = canvas
        self.elements = inkface.loadsvg(KEYBOARD_SVG)
        for e in self.elements:
            self.elements_dict[e.name] = e
            if e.name.startswith('key'):
                e.onTap = self.onTap
                if e.name.endswith('Glow'):
                    e.opacity = 0
                    e.onDraw = self.glowDraw
                    self.glowing_elements[e.name] = 0
                else:
                    e.onDraw = self.defaultDraw

        self.canvas.onTimer = self.onTimer
        self.canvas.timeout = 100

    def onTimer(self):
        for k,v in self.glowing_elements.items():
            if v > 0:
                self.glowing_elements[k] = v - 1
            elif v == 0:
                self.elements_dict[k].opacity = 0
                self.canvas.refresh()

    def onTap(self,e,elements):
        for el in elements:
            if el.name == e.name+'Glow':
                el.opacity = 1
                self.glowing_elements[el.name] = 3 
        
    def defaultDraw(self,e):
        if self.visible:
            self.canvas.draw(e)

    def glowDraw(self,e):
        if self.visible and e.opacity:
            self.canvas.draw(e)

    def onKeyPress(self,txt,code,elements):
        print txt



