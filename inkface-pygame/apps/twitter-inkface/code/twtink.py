

import os
import sys

from inkface.canvas import PygameFace, PygameCanvas
from twtinklib.textbox import TextBox

PREFIX      = '..'
SVG_DIR     = os.path.join(PREFIX,'svg')
THEME_NAME  = 'default'

class App:
    FRAMERATE = 25
    def main(self):
        try:
            self.canvas = PygameCanvas(
                (800,480),framerate = self.FRAMERATE)

            self.entry = PygameFace(
                os.path.join(SVG_DIR,THEME_NAME,'entry.svg'))

            uname = TextBox(
                    border_elem = self.entry.uname_border,
                    txt_elem    = self.entry.uname_txt,
                    cursor_elem = self.entry.uname_cursor,
                    focus_elem  = self.entry.uname_borderfocus,
                    framerate   = self.FRAMERATE)

            passwd = TextBox(
                    border_elem = self.entry.passwd_border,
                    txt_elem    = self.entry.passwd_txt,
                    cursor_elem = self.entry.passwd_cursor,
                    focus_elem  = self.entry.passwd_borderfocus,
                    framerate   = self.FRAMERATE)

            self.entry.loginButton.onLeftClick = self.doLogin

            self.canvas.add(self.entry)

            self.canvas.eventloop()

        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.canvas.stop()
            sys.exit(0)

    def doLogin(self, elem):
        pass

App().main()
