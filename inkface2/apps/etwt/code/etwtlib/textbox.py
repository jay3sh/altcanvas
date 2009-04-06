
from keyboard import Keyboard
import evas

class TextBox:
    def __init__(self, parentApp,
        border_elem, txt_elem, cursor_elem, focus_elem=None,
        framerate=20, mask=None, multiline=False, kbd=None):

        self.parentApp = parentApp
        self.border_elem = border_elem
        self.txt_elem = txt_elem
        self.cursor_elem = cursor_elem
        self.focus_elem = focus_elem
        self.mask = mask
        self.multiline = multiline
        self.flash_count = framerate/3
        self.framerate = framerate
        self.cursor_elem.flcounter = 0

        self.kbd = kbd

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

    def _onKeyPress(self, keyVal):
        print 'reading '+keyVal

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


