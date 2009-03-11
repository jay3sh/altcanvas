import sys
import pygame
from inkface.canvas import PygameFace, PygameCanvas

class TextBox:
    counter_dir = 1
    inFocus = False
    _untouched = True
    mask = None
    def __init__(self, 
        border_elem, txt_elem, cursor_elem, focus_elem, 
        framerate=20, mask=None):

        self.border_elem = border_elem
        self.txt_elem = txt_elem
        self.cursor_elem = cursor_elem
        self.focus_elem = focus_elem
        self.mask = mask
        self.flash_count = framerate/3

        self.cursor_elem.onDraw = self._onCursorDraw
        self.cursor_elem.flcounter = 0

        self.focus_elem.hide()

        self.txt_elem.onKeyPress = self._onKeyPress
        self.border_elem.onKeyPress = self._onKeyPress_proxy
        self.cursor_elem.onKeyPress = self._onKeyPress_proxy

        self.border_elem.onGainFocus = self._onGainFocus
        self.border_elem.onLoseFocus = self._onLoseFocus
        self.txt_elem.onGainFocus = self._onGainFocus
        self.txt_elem.onLoseFocus = self._onLoseFocus
        self.cursor_elem.onGainFocus = self._onGainFocus
        self.cursor_elem.onLoseFocus = self._onLoseFocus

        self.txt_elem.text = self.txt_elem.svg.text
        self.txt_elem.refresh(svg_reload=True)

    def _onKeyPress_proxy(self, elem, event):
        self._onKeyPress(self.txt_elem, event)

    def _onGainFocus(self, elem):
        self.focus_elem.unhide()
        self.inFocus = True
        if self._untouched:
            self.txt_elem.svg.text = ''
            self.txt_elem.text = self.txt_elem.svg.text
            self.txt_elem.refresh(svg_reload=True)
            self._untouched = False

    def _onLoseFocus(self, elem):
        self.focus_elem.hide()
        self.inFocus = False

    def _onKeyPress(self, elem, event):
        if event.key >= pygame.K_SPACE and event.key <= pygame.K_DELETE:
            if self.mask != None:
                elem.svg.text += self.mask
            else:
                elem.svg.text += event.unicode

            elem.text += event.unicode
            elem.refresh(svg_reload=True)
    
            # If the text exceeds width of widget, trim it
            elem_x, elem_y = elem.get_position()
            textbox_x, textbox_y = self.border_elem.get_position()
            elem_x_offset = elem_x - textbox_x

            textbox_width = self.border_elem.svg.w - \
                    self.cursor_elem.svg.w - elem_x_offset
            while (elem_x_offset + elem.svg.w) > textbox_width:
                elem.svg.text = elem.svg.text[1:]
                elem.refresh(svg_reload=True)

        elif event.key == pygame.K_BACKSPACE:
            elem.text = elem.text[:-1]
            elem.svg.text = elem.svg.text[:-1]
            elem.refresh(svg_reload=True)
            # TODO handle underrun

        elif event.key == pygame.K_ESCAPE:
            pass

    def _onCursorDraw(self, elem):
        if not self.inFocus:
            elem.hide()
            return
        txt_x, txt_y = self.txt_elem.get_position()
        elem_x = txt_x + self.txt_elem.svg.w + 2
        elem_y = txt_y
        elem.set_position((elem_x,elem_y))

        if abs(elem.flcounter) >= self.flash_count:
            if self.counter_dir > 0:
                elem.hide()
            else:
                elem.unhide()
            self.counter_dir = -1 * self.counter_dir

        elem.flcounter += self.counter_dir
 
    def set_text(self, text):
        self.txt_elem.text = text
        if self.mask == None:
            self.txt_elem.svg.text = text
        else:
            self.txt_elem.svg.text = self.mask * len(text)

        self.txt_elem.refresh(svg_reload=True)

    def get_text(self):
        return self.txt_elem.text
        

