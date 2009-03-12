

import os
import sys
import pickle
import getopt

from inkface.canvas import PygameFace, PygameCanvas
from twtinklib.textbox import TextBox
from twtinklib.twt import Twt
from twtinklib.utils import encrypt,decrypt

TWITINK_RC      = os.environ['HOME']+os.sep+'.twitinkrc'
PREFIX      = '..'
SVG_DIR     = os.path.join(PREFIX,'svg')

class App:
    FRAMERATE = 25
    def main(self, theme='default'):
        try:
            self.canvas = PygameCanvas(
                (800,480),framerate = self.FRAMERATE)

            self.theme = theme
            self.entry = PygameFace(
                os.path.join(SVG_DIR,self.theme,'entry.svg'))

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

            try:
                username, password = self.load_config()
            except:
                username = None
                password = None

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
            os.path.join(SVG_DIR, self.theme, 'twits.svg'))

        twt = Twt(username, password, self.twits, self.canvas)

        # Login was successful, let's save credentials.
        self.save_config(username, password)

        self.canvas.remove(self.entry)

        twt.load()

def usage():
    print 'Twitter Inkface client:'
    print ' twitink.py [options]'
    print ' '
    print ' -t --theme  : Theme to use for the app'
    print ' -h --help   : usage'


if __name__ == '__main__':
    try:
        optlist, args = getopt.getopt(sys.argv[1:],'ht:',['help','theme='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(0)

    theme = 'default'
    for o,a in optlist:
        if o in ('-h','--help'):
            usage()
            break
        elif o in ('-t','--theme'):
            theme = a
 
    App().main(theme=theme)
