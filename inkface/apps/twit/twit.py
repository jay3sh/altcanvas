#!/usr/bin/python

import os
import re
import threading
import urllib2
import pickle

import cairo

import inkface
import inklib
import twitink.twitter

from twitink.keyboard import Keyboard
from twitink.login import LoginGui
from twitink.imgloader import ImageLoader
from twitink.twit import TwitGui
from twitink.utils import encrypt

import sys

SVG_DIR         = '/usr/share/pixmaps/twitink/'
LOGIN_SVG       = SVG_DIR+'login.svg'
PUBLIC_SVG      = SVG_DIR+'public.svg'
KEYBOARD_SVG    = SVG_DIR+'keyboard.svg'

TWITINK_RC      = os.environ['HOME']+os.sep+'.twitinkrc'

#
# Control Flow
# 

class TwitterApp:
    def __init__(self):
        self.canvas = inkface.create_X_canvas(fullscreen=True)
        self.kbd = Keyboard(self.canvas,KEYBOARD_SVG)

    def main(self):
        self.loginGui = LoginGui(self.canvas,LOGIN_SVG,kbd=self.kbd)
        self.loginGui.resultProcessor = self.onLoginSuccess
        self.canvas.add(self.loginGui)

        self.canvas.eventloop()
        
    def onLoginSuccess(self,twitterApi):
        self.canvas.remove(self.loginGui)

        if self.loginGui.save_creds_flag:
            pfile = open(TWITINK_RC,'w')
            m = {}
            m['username'] = self.loginGui.username
            m['password'] = encrypt(self.loginGui.password)
            pickle.dump(m,pfile)

        del self.loginGui

        self.twitGui = TwitGui(self.canvas,PUBLIC_SVG,
                            twitterApi,kbd=self.kbd)
        self.twitGui.resultProcessor = self.onExit
        self.canvas.add(self.twitGui)
        self.canvas.refresh()

        self.twitGui.loadTimeline(self.twitGui.FRIENDS_TIMELINE)
        self.twitGui.loadTimeline(self.twitGui.PUBLIC_TIMELINE)

        self.twitGui.turnOffLoadingLabel()

    def onExit(self,user_data=None):
        self.canvas.remove(self.twitGui)
        del self.twitGui
        inkface.exit()


if __name__ == '__main__':
    #import cProfile
    #cProfile.run('TwitterApp().main()','twit.prof')
    TwitterApp().main()


