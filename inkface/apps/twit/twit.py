#!/usr/bin/python

import os
import re
import threading
import urllib2

import cairo

import inkface
import inklib
import twitink.twitter

from twitink.keyboard import Keyboard
from twitink.login import LoginGui
from twitink.imgloader import ImageLoader
from twitink.twit import TwitGui

import sys

#
# Control Flow
# 

class TwitterApp:
    def __init__(self):
        self.canvas = inkface.create_X_canvas(fullscreen=False)
        self.kbd = Keyboard(self.canvas)

    def main(self):
        self.loginGui = LoginGui(self.canvas,'login.svg',kbd=self.kbd)
        self.loginGui.resultProcessor = self.onLoginSuccess
        self.canvas.add(self.loginGui)

        self.canvas.eventloop()
        
    def onLoginSuccess(self,twitterApi):
        self.canvas.remove(self.loginGui)
        del self.loginGui

        self.twitGui = TwitGui(self.canvas,'public.svg',
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


