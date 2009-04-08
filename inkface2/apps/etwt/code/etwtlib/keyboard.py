
from inkface.evas import EFace
from etwtlib.inkobject import InkObject

class Keyboard(InkObject):
    K_BACKSPACE = 8
    number_row_caps = map(lambda x: 'key_' + x,
        ('Exclaim', 'At', 'Pound', 'Dollar', 'Percent',
        'Caret', 'Amp', 'Asterisk', 'LeftParen', 'RightParen'))

    symbol_row = map(lambda x: 'key_' + x,
        ('Dash', 'Equal', 'LeftSqParen', 'RightSqParen', 'Backslash',
        'Semicolon', 'SinQuote', 'Comma', 'Period', 'FrontSlash'))

    symbol_row_caps = map(lambda x: 'key_' + x,
        ('UnderScore', 'Plus', 'LeftBrace', 'RightBrace', 'Pipe',
        'Colon', 'DblQuote', 'Lt', 'Rt', 'QMark'))

    special_keys = number_row_caps + symbol_row + symbol_row_caps
    special_keys.append('key_Enter')
    special_keys.append('key_Space')
    special_keys.append('key_Caps')
    special_keys.append('key_Backspace')

    symbol_map = \
        {
            'key_Exclaim'       :   '!',
            'key_At'            :   '@',
            'key_Pound'         :   '#',
            'key_Dollar'        :   '$',
            'key_Percent'       :   '%',
            'key_Caret'         :   '^',
            'key_Amp'           :   '&',
            'key_Asterisk'      :   '*',
            'key_LeftParen'     :   '(',
            'key_RightParen'    :   ')',
            'key_Dash'          :   '-',
            'key_Equal'         :   '=',
            'key_LeftSqParen'   :   '[',
            'key_RightSqParen'  :   ']',
            'key_Backslash'     :   '\\',
            'key_Semicolon'     :   ';',
            'key_SinQuote'      :   '\'',
            'key_Comma'         :   ',',
            'key_Period'        :   '.',
            'key_FrontSlash'    :   '/',
            'key_UnderScore'    :   '_',
            'key_Plus'          :   '+',
            'key_LeftBrace'     :   '{',
            'key_RightBrace'    :   '}',
            'key_Pipe'          :   '|',
            'key_Colon'         :   ':',
            'key_DblQuote'      :   '"',
            'key_Lt'            :   '<',
            'key_Rt'            :   '>',
            'key_QMark'         :   '?',
            'key_Space'         :   ' '
        }

    def __init__(self, svgname, canvas):
        InkObject.__init__(self)

        self.face = EFace(svgname, canvas)

        self._capsLockOff()

        self.face.closeButton.onLeftClick = self.onClose

        for e in self.face.elements:
            if e.svg.label not in ('closeButton','kbdBackground'):
                e.onLeftClick = self.onKeyClick


    def onKeyClick(self, elem):
        assert elem.svg is not None and elem.svg.label is not None
        keyValue = elem.svg.label
        if keyValue[3] == '_':
            if keyValue == 'key_Enter':
                self.emit('done')
            elif keyValue == 'key_Caps':
                if self._capsLock:
                    self._capsLockOff()
                else:
                    self._capsLockOn()
            elif keyValue == 'key_Backspace':
                self.emit('keypress', self.K_BACKSPACE)
            elif self.symbol_map.has_key(keyValue):
                self.emit('keypress',self.symbol_map[keyValue])
        else:
            self.emit('keypress', keyValue[3])

    def onEnter(self, elem):
        self.emit('done')

    def onClose(self, elem):
        self.hide()

    def hide(self):
        for e in self.face.elements:
            e.hide()

    def unhide(self):
        if self._capsLock:
            self._capsLockOn()
        else:
            self._capsLockOff()

    def onCapsLock(self, elem):
        self._capsLockOn()

    def _capsLockOn(self):
        for e in self.face.elements:
            if e.svg is not None and \
                e.svg.label is not None and \
                (e.svg.label in self.symbol_row or
                    e.svg.label[3].islower() or
                    e.svg.label[3].isdigit()):

                e.hide()
            else:
                e.unhide()

        self.face.kbdBackground.unhide()
        self.face.closeButton.unhide()
        self._capsLock = True

    def _capsLockOff(self):
        for e in self.face.elements:
            if e.svg is not None and \
                e.svg.label is not None and \
                (e.svg.label in self.number_row_caps or \
                    e.svg.label in self.symbol_row_caps or \
                    e.svg.label[3].isupper()):

                e.hide()
            else:
                e.unhide()

        self.face.kbdBackground.unhide()
        self.face.closeButton.unhide()
        self._capsLock = False
