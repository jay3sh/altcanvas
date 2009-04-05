
import evas

class TextBox:
    def __init__(self,
        border_elem, txt_elem, cursor_elem, focus_elem=None,
        framerate=20, mask=None, multiline=False):

        self.border_elem = border_elem
        self.txt_elem = txt_elem
        self.cursor_elem = cursor_elem
        self.focus_elem = focus_elem
        self.mask = mask
        self.multiline = multiline
        self.flash_count = framerate/3
        self.framerate = framerate


        if self.focus_elem:
            self.focus_elem.hide()

        self.border_elem.onGainFocus = self._onGainFocus
        self.border_elem.onLoseFocus = self._onLoseFocus

    def _onGainFocus(self, elem):
        if self.focus_elem is not None:
            self.focus_elem.unhide()

    def _onLoseFocus(self, elem):
        if self.focus_elem is not None:
            self.focus_elem.hide()
