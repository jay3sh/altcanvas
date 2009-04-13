
from keyboard import Keyboard
from inkface.widgets.inkobject import InkObject

class Textbox(InkObject):
    '''
    A textbox widget. 

    This widget can be realized by passing at least three \
    :class:`inkface.altsvg.element.Element` objects to its constructor - \
    border, txt, cursor.

    :param border_elem: An SVG element that defines the boundary of the \
    textbox. If the text exceeds this boundaries of this element, then \
    it is automatically truncated (only visually) or wrapped.
    :param txt_elem: A text SVG element whose text will modified to what \
    user inputs. 
    :param cursor_elem: A cursor element which will blink at submultiple rate \
    of framerate
    :param focus_elem: An optional element which will appear when the textbox \
    has focus.
    :param keyfocus: A keyfocus object. (TBD)
    :param framerate: framerate in FPS
    :param mask: A mask character, in case one wants to hide the text.
    :param multiline: Not supported yet.
    :param kbd: A virtual keyboard widget \
    :class:`inkface.widgets.keyboard.Keyboard`
    '''
    def __init__(self, 
        border_elem, txt_elem, cursor_elem, 
        keyfocus=None, focus_elem=None,
        framerate=25, mask=None, multiline=False, kbd=None):

        InkObject.__init__(self)

        self.keyfocus = keyfocus 
        self.border_elem = border_elem
        self.txt_elem = txt_elem
        self.txt_elem.text = ''
        self.cursor_elem = cursor_elem
        self.focus_elem = focus_elem
        self.mask = mask
        self.multiline = multiline
        self.flash_count = framerate/3
        self.framerate = framerate
        self.cursor_elem.flcounter = 0

        self.kbd = kbd

        self._untouched = True

        self.counter_dir = 1
        self.inFocus = False

        if self.focus_elem:
            self.focus_elem.hide()

        self.border_elem.onMouseGainFocus = self._onMouseGainFocus

        self.cursor_elem.onDraw = self._onCursorDraw

    def _onCursorDraw(self, elem):
        if not self.inFocus:
            elem.hide()
            return True
        if abs(elem.flcounter) >= self.flash_count:
            if self.counter_dir > 0:
                elem.hide()
            else:
                elem.unhide()
            self.counter_dir = -1 * self.counter_dir

        elem.flcounter += self.counter_dir

        return True
 
    def _onMouseGainFocus(self, elem):
        if self.inFocus:
            # avoid multiple focus gain calls
            return

        # Claim the keyfocus first
        if self.keyfocus is not None:
            self.keyfocus.get(self._onKeyLoseFocus)

        self.inFocus = True
        if self.focus_elem is not None:
            self.focus_elem.unhide()

        # Display the keyboard
        self.kbd.unhide()
        self.kbd.connect('keypress',self._onKeyPress)
        self.kbd.connect('done',self._onKeyboardDone)

        if self._untouched:
            self.border_elem.refresh(svg_reload=False)
            self.txt_elem.svg.text = ''
            self.txt_elem.text = self.txt_elem.svg.text
            self.txt_elem.refresh()
            self._untouched = False

    def _onKeyPress(self, keyVal):
        self.border_elem.refresh(svg_reload=False)
        elem = self.txt_elem

        if keyVal == Keyboard.K_BACKSPACE:
            elem.text = elem.text[:-1]
            elem.svg.text = elem.svg.text[:-1]
        else:
            if self.mask != None:
                elem.svg.text += self.mask
            else:
                elem.svg.text += keyVal
            elem.text += keyVal

        elem.refresh(svg_reload=True)

        if not self.multiline:
            elem_x, elem_y = elem.get_position()
            textbox_x, textbox_y = self.border_elem.get_position()
            elem_x_offset = elem_x - textbox_x

            text_width = self.border_elem.svg.w - \
                    self.cursor_elem.svg.w - elem_x_offset
            while (elem_x_offset + elem.svg.w) > text_width:
                elem.svg.text = elem.svg.text[1:]
                elem.refresh()
        else:
            pass

        self.emit('changed', elem.text)

    def _onKeyboardDone(self):
        if self.keyfocus is not None:
            self.keyfocus.put()
        self._onKeyLoseFocus()

    def _onKeyLoseFocus(self):
        self.inFocus = False
        self.kbd.disconnect('keypress',self._onKeyPress)
        self.kbd.disconnect('done', self._onKeyboardDone)
        if self.focus_elem is not None:
            self.focus_elem.hide()
        self.kbd.hide()

    def set_text(self, text):
        '''
        Set the text contents of this textbox

        :param text: Text string to be set
        '''
        self.border_elem.refresh(svg_reload=False)
        self.txt_elem.text = text
        if self.mask == None:
            self.txt_elem.svg.text = text
        else:
            self.txt_elem.svg.text = self.mask * len(text)

        self.txt_elem.refresh(svg_reload=True)
        self._untouched = False

    def get_text(self):
        '''
        Get the current text content of this textbox.

        :rtype: Text string 
        '''
        return self.txt_elem.text

