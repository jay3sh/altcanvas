

import os
import sys
import pickle

from inkface.canvas import PygameFace, PygameCanvas
from twtinklib.textbox import TextBox
from twtinklib.twt import Twt
from twtinklib.utils import encrypt,decrypt

TWITINK_RC      = os.environ['HOME']+os.sep+'.twitinkrc'
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

            self.uname = TextBox(
                    border_elem = self.entry.uname_border,
                    txt_elem    = self.entry.uname_txt,
                    cursor_elem = self.entry.uname_cursor,
                    focus_elem  = self.entry.uname_borderfocus,
                    framerate   = self.FRAMERATE)

            self.passwd = TextBox(
                    border_elem = self.entry.passwd_border,
                    txt_elem    = self.entry.passwd_txt,
                    cursor_elem = self.entry.passwd_cursor,
                    focus_elem  = self.entry.passwd_borderfocus,
                    framerate   = self.FRAMERATE,
                    mask        = '*')

            self.entry.loginButton.onLeftClick = self.doLogin

            username, password = self.load_config()

            if username and password:
                self.uname.set_text(username)
                self.passwd.set_text(password)

            self.canvas.add(self.entry)

            self.canvas.eventloop()

        except Exception, e:
            import traceback
            print traceback.format_exc()
            self.canvas.stop()
            sys.exit(0)

    def load_config(self):
        config = None
        try:
            pfile = open(TWITINK_RC,'r')
            config = pickle.load(pfile)
        except IOError,ioe:
            print '.twitinkrc file not found'

        if config:
            return(config['username'],decrypt(config['password']))

    def save_config(self, username, password):
        pfile = open(TWITINK_RC,'w')
        m = {}
        m['username'] = username
        m['password'] = encrypt(password)
        pickle.dump(m,pfile)

    def doLogin(self, elem):
        username = self.uname.get_text()
        password = self.passwd.get_text()

        self.twits = PygameFace(
            os.path.join(SVG_DIR, THEME_NAME, 'twits.svg'))

        twt = Twt(username, password, self.twits, self.canvas)

        # Login was successful, let's save credentials.
        self.save_config(username, password)

        self.canvas.remove(self.entry)

        twt.load()

App().main()
