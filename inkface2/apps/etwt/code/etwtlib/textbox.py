
from keyboard import Keyboard
import evas

class TextBox:
    def __init__(self, parentApp,
        border_elem, txt_elem, cursor_elem, focus_elem=None,
        framerate=20, mask=None, multiline=False, kbd=None):


        self.parentApp = parentApp
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
        self.parentApp.keyfocus.get(self._onKeyLoseFocus)

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

        elem.refresh()

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

    def _onKeyboardDone(self):
        self.parentApp.keyfocus.put()
        self._onKeyLoseFocus()

    def _onKeyLoseFocus(self):
        self.inFocus = False
        self.kbd.disconnect('keypress',self._onKeyPress)
        self.kbd.disconnect('done', self._onKeyboardDone)
        if self.focus_elem is not None:
            self.focus_elem.hide()
        self.kbd.hide()


