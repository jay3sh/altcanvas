
import inkface
import inklib
import twitter
from keyboard import Keyboard
import os

import sys

class LoginGui(inklib.Face):
    username = os.environ['TWT_USERNAME']
    password = os.environ['TWT_PASSWORD']
    def __init__(self,canvas,svgname):
        print 'i --> %d'%sys.getrefcount(self)
        inklib.Face.__init__(self,canvas,svgname)

        print 'i --> %d'%sys.getrefcount(self)
        self.kbd = Keyboard(self.canvas)

        print 'i --> %d'%sys.getrefcount(self)
        self.closeButton.onTap = self.onExit
        self.loginButton.onTap = self.onLogin
        self.usernameFrame.onTap = self.onUsernameTap
        self.usernameText.onTap = self.onUsernameTap
        self.passwordFrame.onTap = self.onPasswordTap
        self.passwordText.onTap = self.onPasswordTap
        
        print 'i --> %d'%sys.getrefcount(self)
        self.usernameText.text = self.username
        self.usernameText.refresh()
        self.passwordText.text = '*'*len(self.password)
        self.passwordText.refresh()

        print 'i --> %d'%sys.getrefcount(self)

    def populateUsername(self,txt):
        self.username = txt
        self.usernameText.text = txt
        self.usernameText.refresh()

    def populatePassword(self,txt):
        self.password = txt
        self.passwordText.text = '*'*len(txt)
        self.passwordText.refresh()

    def onUsernameTap(self,e):
        self.kbd.resultProcessor = self.populateUsername
        self.kbd.reset()
        self.canvas.add(self.kbd)

    def onPasswordTap(self,e):
        self.kbd.resultProcessor = self.populatePassword
        self.kbd.reset()
        self.canvas.add(self.kbd)
        
    def onLogin(self,e):
        twitterApi = twitter.Api(username=self.username,password=self.password)
        self.resultProcessor(twitterApi)
       
    def onExit(self,e):
        inkface.exit()


