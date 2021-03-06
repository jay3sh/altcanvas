
import os
import pickle

from urllib2 import HTTPError

from inkface.evas import EFace, ECanvas

from inkface.widgets.inkobject import InkObject
from inkface.widgets.textbox import Textbox
from inkface.widgets.keyboard import Keyboard

from etwtlib.twt import Twt
from etwtlib.utils import encrypt,decrypt
from etwtlib.constants import *


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
    def __init__(self, theme):
        InkObject.__init__(self)

        self.theme = theme
        self.face = EFace(
            os.path.join(SVG_DIR,self.theme,'entry.svg'))

        self.canvas = ECanvas(
                            (int(float(self.face.svg.width)),
                            int(float(self.face.svg.height))),
                            framerate = FRAMERATE)


    def load(self):
        self.face.load_elements(self.canvas)

        self.face.waitIcon.hide()
        self.face.authfailIcon.hide()

        kbd_face = EFace(
                    os.path.join(SVG_DIR, self.theme, 'keyboard.svg'), 
                    self.canvas)

        self.kbd = Keyboard(kbd_face)
        self.kbd.hide()

        self.keyfocus = KeyFocus()

        self.uname = Textbox(
                keyfocus    = self.keyfocus,
                border_elem = self.face.uname_border,
                txt_elem    = self.face.uname_txt,
                cursor_elem = self.face.uname_cursor,
                focus_elem  = self.face.uname_borderfocus,
                framerate   = FRAMERATE,
                kbd         = self.kbd)

        self.passwd = Textbox(
                keyfocus    = self.keyfocus,
                border_elem = self.face.passwd_border,
                txt_elem    = self.face.passwd_txt,
                cursor_elem = self.face.passwd_cursor,
                focus_elem  = self.face.passwd_borderfocus,
                framerate   = FRAMERATE,
                mask        = '*',
                kbd         = self.kbd)

        self.face.friendsLogin.onLeftClick = self.doFriendsLogin
        self.face.publicLogin.onLeftClick = self.doPublicLogin
        self.face.repliesLogin.onLeftClick = self.doRepliesLogin

        self.face.exitButton.onLeftClick = self.Exit

        try:
            username, password = self.load_config()
        except:
            username = None
            password = None

        if username and password:
            self.uname.set_text(username)
            self.passwd.set_text(password)


    def doFriendsLogin(self, elem):
        self.doLogin(Twt.TWT_FRIENDS)

    def doPublicLogin(self, elem):
        self.doLogin(Twt.TWT_PUBLIC)

    def doRepliesLogin(self, elem):
        self.doLogin(Twt.TWT_REPLIES)

    def doLogin(self, twt_type):
        self.face.waitIcon.unhide()
        self.face.authfailIcon.hide()

        username = self.uname.get_text()
        password = self.passwd.get_text()

        try:
            twt = Twt(username, password, self.theme, 
                        self.canvas, twt_type=twt_type)
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


     
