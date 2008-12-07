
import inkface
import inklib

KEYBOARD_SVG='keyboard.svg'

class Keyboard(inklib.Face):
    visible = False
    glowing_elements = {}
    def __init__(self,canvas):
        #self.canvas = canvas
        #self.elements = inkface.loadsvg(KEYBOARD_SVG)
        inklib.Face.__init__(self,canvas,KEYBOARD_SVG)

        for k,e in self.elements.items():
            if e.name.startswith('key'):
                e.onTap = self.onTap
                if e.name.endswith('Glow'):
                    e.opacity = 0
                    e.onDraw = self.glowDraw
                    self.glowing_elements[e.name] = 0

        self.keyEnter.onTap = self.onEnter
        self.canvas.onTimer = self.onTimer
        self.canvas.timeout = 100

    def onTimer(self):
        for k,v in self.glowing_elements.items():
            if v > 0:
                self.glowing_elements[k] = v - 1
            elif v == 0:
                self.elements[k].opacity = 0
                self.canvas.refresh()

    def onTap(self,e):
        try:
            ge = self.elements[e.name+'Glow']
            if ge: 
                ge.opacity = 1
                self.glowing_elements[ge.name] = 3
        except KeyError,ke:
            pass

    def onEnter(self,e):
        self.canvas.remove(self)
        self.canvas.refresh()
        
    def glowDraw(self,e):
        if e.opacity:
            self.canvas.draw(e)

    def onKeyPress(self,txt,code,elements):
        print txt



