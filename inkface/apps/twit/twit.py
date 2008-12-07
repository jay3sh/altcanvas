#!/usr/bin/python

import inkface
import inklib
import twitter
from keyboard import Keyboard

import os

class LoginGui(inklib.Face):
    username = os.environ['TWT_USERNAME']
    password = os.environ['TWT_PASSWORD']
    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)

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

class TwitGui(inklib.Face):
    twtApi = None
    PUBLIC_TIMELINE = 0
    FRIENDS_TIMELINE = 1

    cloud_pattern = 'publicCloud(\d+)'
    twt_pattern = 'publicTwt(\d+)'

    def __init__(self,canvas,svgname,api):
        inklib.Face.__init__(self,canvas,svgname)

        self.twitButton.onTap = self.onTwit
        self.quitButton.onTap = self.onExit

        self.kbd = Keyboard(self.canvas)

        self.twtApi = api

        for name,elem in self.elements.items():
            #if name.startswith('publicTwt') or name.startswith('publicCloud'):
            if name.startswith('publicCloud'):
                elem.onTap = self.FocusTwt

    def FocusTwt(self,e):
        import re
        m = re.match(self.cloud_pattern,e.name) or re.match(self.twt_pattern,e.name)
        if m:
            num = m.group(1)
            self.canvas.reset_order()
            self.canvas.bring_to_front(self.elements['publicCloud'+str(num)])
            self.canvas.bring_to_front(self.elements['publicTwt'+str(num)])
            self.canvas.bring_to_front(self.twitButton)
            self.canvas.bring_to_front(self.quitButton)
            self.canvas.bring_to_front(self.friendsButton)
            self.canvas.bring_to_front(self.publicButton)

    def loadTimeline(self,type):

        if type == self.PUBLIC_TIMELINE:
            LINE_LIMIT = 25 
            elem_prefix = 'publicTwt'
            twt_list = self.twtApi.GetPublicTimeline()
        else:
            LINE_LIMIT = 60
            elem_prefix = 'friendTwt'
            twt_list = self.twtApi.GetFriendsTimeline()

        i = 0
        for name,elem in self.elements.items():
            j = 1
            twt_text = ''
            if name.startswith(elem_prefix):

                # Iterate till we get an ascii string
                while True:
                    try:
                        ascii_twt = str(twt_list[i].text)
                    except UnicodeEncodeError, uee:
                        i += 1
                    except IndexError, ie:
                        self.canvas.refresh()
                        return
                    else:
                        break

                # Chop the ascii tweet into multiple lines
                for c in ascii_twt:
                    if j%LINE_LIMIT == 0:
                        twt_text += '\n'+c
                    else:
                        twt_text += c
                    j += 1    

                elem.text = twt_text
                elem.refresh()
                i += 1

        self.canvas.refresh()
        
    def onExit(self,e):
        inkface.exit()

    def onTwit(self,e):
        self.canvas.add(self.kbd)
        self.canvas.refresh()
        
#
# Control Flow
# 

class TwitterApp:
    def __init__(self):
        self.canvas = inkface.create_X_canvas()

    def main(self):
        self.loginGui = LoginGui(self.canvas,'login.svg')
        self.loginGui.resultProcessor = self.onLoginSuccess
        self.canvas.add(self.loginGui)

        self.canvas.eventloop()
        
    def onLoginSuccess(self,twitterApi):
        self.canvas.remove(self.loginGui)
        self.twitGui = TwitGui(self.canvas,'public.svg',twitterApi)
        self.canvas.add(self.twitGui)
        self.canvas.refresh()
        self.twitGui.loadTimeline(self.twitGui.FRIENDS_TIMELINE)
        self.twitGui.loadTimeline(self.twitGui.PUBLIC_TIMELINE)


if __name__ == '__main__':
    TwitterApp().main()


