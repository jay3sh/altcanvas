
import os
import pickle

from urllib2 import HTTPError

from inkface.evas import EFace, ECanvas
from etwtlib.textbox import TextBox
from etwtlib.keyboard import Keyboard
from etwtlib.twt import Twt
from etwtlib.utils import encrypt,decrypt
from etwtlib.constants import *

from etwtlib.inkobject import InkObject

class KeyFocus:
    loseFocus = None
    def get(self, callback):
        if self.loseFocus is not None:
            self.loseFocus()
        self.loseFocus = callback
        return True

    def put(self):
        self.loseFocus = None
 

class Entry(InkObject):
    def __init__(self, canvas, theme):
        InkObject.__init__(self)

        self.canvas = canvas
        self.theme = theme

    def load(self):
        self.face = EFace(
            os.path.join(SVG_DIR,self.theme,'entry.svg'), self.canvas)

        self.face.waitIcon.hide()
        self.face.authfailIcon.hide()

        self.kbd = Keyboard(
            os.path.join(SVG_DIR, self.theme, 'keyboard.svg'), self.canvas)
        self.kbd.hide()

        self.keyfocus = KeyFocus()

        self.uname = TextBox(
                keyfocus    = self.keyfocus,
                border_elem = self.face.uname_border,
                txt_elem    = self.face.uname_txt,
                cursor_elem = self.face.uname_cursor,
                focus_elem  = self.face.uname_borderfocus,
                framerate   = FRAMERATE,
                kbd         = self.kbd)

        self.passwd = TextBox(
                keyfocus    = self.keyfocus,
                border_elem = self.face.passwd_border,
                txt_elem    = self.face.passwd_txt,
                cursor_elem = self.face.passwd_cursor,
                focus_elem  = self.face.passwd_borderfocus,
                framerate   = FRAMERATE,
                mask        = '*',
                kbd         = self.kbd)

        self.face.loginButton.onLeftClick = self.doLogin

        self.face.exitButton.onLeftClick = self.Exit

        try:
            username, password = self.load_config()
        except:
            username = None
            password = None

        if username and password:
            self.uname.set_text(username)
            self.passwd.set_text(password)

    def doLogin(self, elem):
        username = self.uname.get_text()
        password = self.passwd.get_text()

        try:
            self.face.authfailIcon.hide()
            self.face.waitIcon.unhide()
            twt = Twt(username, password, self.theme, self.canvas)
        except HTTPError, hter:
            self.face.waitIcon.hide()
            self.face.authfailIcon.unhide()
            return

        # Login was successful, let's save credentials.
        self.save_config(username, password)

        self.face.waitIcon.hide()

        self.canvas.remove(self.face)

        twt.load()

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

    def Exit(self, elem):
        self.canvas.stop()


     
