
import inkface
import inklib
import twitter
from keyboard import Keyboard
import os

import sys

class LoginGui(inklib.Face):
    username = 'username'
    password = 'password'
    save_creds_flag = False

    def __init__(self,canvas,svgname,kbd=None,username=None,password=None):
        inklib.Face.__init__(self,canvas,svgname)

        if username:
            self.username = username
        if password:
            self.password = password

        if kbd:
            self.kbd = kbd
        else:
            self.kbd = Keyboard(self.canvas)
            

        self.closeButton.onTap = self.onExit
        self.loginButton.onTap = self.onLogin
        self.usernameFrame.onTap = self.onUsernameTap
        self.usernameText.onTap = self.onUsernameTap
        self.passwordFrame.onTap = self.onPasswordTap
        self.passwordText.onTap = self.onPasswordTap
        
        self.usernameText.text = self.username
        self.usernameText.refresh()
        self.passwordText.text = '*'*len(self.password)
        self.passwordText.refresh()

        self.saveTick.onDraw = self.donotdraw

        self.buttonSave.onTap = self.setSaveCreds

    def setSaveCreds(self,e):
        self.saveTick.onDraw = self.dodraw
        self.save_creds_flag = True
        self.canvas.refresh()
    
    def saveCreds(self,e):
        pass

    def donotdraw(self,e):
        pass

    def dodraw(self,e):
        self.canvas.draw(e)

    def populateUsername(self,txt):
        if txt:
            self.username = txt
            self.usernameText.text = txt
            self.usernameText.refresh()
        self.canvas.remove(self.kbd)
        self.canvas.refresh()

    def populatePassword(self,txt):
        if txt:
            self.password = txt
            self.passwordText.text = '*'*len(txt)
            self.passwordText.refresh()
        self.canvas.remove(self.kbd)
        self.canvas.refresh()

    def onUsernameTap(self,e):
        self.kbd.resultProcessor = self.populateUsername
        self.kbd.hidetext = False
        self.kbd.reset()
        self.canvas.add(self.kbd)

    def onPasswordTap(self,e):
        self.kbd.resultProcessor = self.populatePassword
        self.kbd.reset()
        self.kbd.hidetext = True 
        self.canvas.add(self.kbd)
        
    def onLogin(self,e):
        self.loginButtonShadow.onDraw = self.donotdraw
        self.canvas.refresh()

        twitterApi = twitter.Api(username=self.username,password=self.password)
        self.resultProcessor(twitterApi)
       
    def onExit(self,e):
        inkface.exit()


