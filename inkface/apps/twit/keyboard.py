
import inkface
import inklib
import re

#KEYBOARD_SVG='keyboard.svg'
KEYBOARD_SVG='keyboard-lite.svg'

special_key_map = {
    'Tilde':'~',
    'Period':'.',
    'Comma':',',
    'SemiColon':';',
    'Question':'?',
    'Exclaim':'!',
    'At':'@',
    'Pound':'#',
    'Dollar':'$',
    'Percent':'%',
    'Star':'*',
    'Asterisk':'*',
    'SQuote':'\'',
    'DQuote':'"',
    'LPara':'(',
    'RPara':')',
    'LSqBracket':'[',
    'RSqBracket':']',
    'FSlash':'/',
    'BSlash':'\\',
    'Amp':'&',
    'Caret':'^',
    'Equal':'=',
    'Minus':'-',
    'Plus':'+'
    }


class Keyboard(inklib.Face):
    glowing_elements = {}
    hidetext = False
    typedtext = ''
    def __init__(self,canvas):
        inklib.Face.__init__(self,canvas,KEYBOARD_SVG)

        for k,e in self.elements.items():
            if e.name.startswith('keySp') and not e.name.endswith('Glow'):
                pass
            elif e.name.startswith('key'):
                if e.name.endswith('Glow'):
                    e.opacity = 0
                    self.glowing_elements[e.name] = 0

        self.keyboardText.text = ''
        self.keyboardText.refresh()

        self.wire()


    def wire(self):
        for k,e in self.elements.items():
            if e.name.startswith('keySp') and not e.name.endswith('Glow'):
                e.onTap = self.onSpecialKey;
            elif e.name.startswith('key'):
                if e.name.endswith('Glow'):
                    e.onDraw = self.glowDraw
                else:
                    e.onTap = self.onAlNumTap

        self.keySpace.onTap = self.onSpace
        self.keyEnter.onTap = self.onEnter
        self.keyCancel.onTap = self.onCancel
        self.keyBackspace.onTap = self.onBackspace
        self.keyboardText.onKeyPress = self.onKeyPress

        self.keyboardText.onTap = None
        self.keyboardEntry.onTap = None

        #self.canvas.onTimer = self.onTimer
        #self.canvas.timeout = 100
       
    def onSpecialKey(self,e):
        m = re.match('keySp(\w+)',e.name)

        if not m: return 

        keyName = m.group(1)
        try:
            keyLetter = special_key_map[keyName] 
        except KeyError,ke:
            pass

        if not keyLetter: return

        if self.hidetext:
            self.keyboardText.text += '*'
            self.typedtext += keyLetter
        else:
            self.keyboardText.text += keyLetter
            self.typedtext += keyLetter

        self.keyboardText.refresh()
        self.canvas.refresh()
        
    def onBackspace(self,e):
        self.keyboardText.text = self.keyboardText.text[:-1]
        self.typedtext = self.typedtext[:-1]
        self.keyboardText.refresh()
        self.canvas.refresh()
        
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
        if self.hidetext:
            self.keyboardText.text += '*'
            self.typedtext += letter
        else:
            self.keyboardText.text += letter
            self.typedtext += letter

        self.keyboardText.refresh()
        try:
            ge = self.elements[e.name+'Glow']
            if ge: 
                ge.opacity = 0
                self.glowing_elements[ge.name] = 3
        except KeyError,ke:
            pass
        self.canvas.refresh()

    def onEnter(self,e):
        self.resultProcessor(self.typedtext)
        
    def onCancel(self,e):
        self.resultProcessor(None)

    def glowDraw(self,e):
        if e.opacity:
            self.canvas.draw(e)

    def reset(self):
        self.keyboardText.text = ''
        self.typedtext = ''
        self.keyboardText.refresh()

    def onKeyPress(self,e,txt,keycode):
        
        if self.hidetext:
            self.keyboardText.text += '*'
            self.typedtext += txt.strip()
        else:
            self.keyboardText.text += txt.strip()
            self.typedtext += txt.strip()

        # Special keys
        if keycode == inkface.KeyEscape:
            self.onCancel(e)
        if keycode == inkface.KeyBackspace:
            self.onBackspace(e)
        elif keycode == inkface.KeySpace:
            if self.hidetext:
                self.keyboardText.text += '*'
                self.typedtext += ' '
            else:
                self.keyboardText.text += ' '
                self.typedtext += ' '
        elif keycode == inkface.KeyEnter:
            self.onEnter(e)

        self.keyboardText.refresh()
        self.canvas.refresh()



