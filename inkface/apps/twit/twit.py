#!/usr/bin/python

import inkface
import inklib
import twitter
from keyboard import Keyboard

import os

class LoginGui(inklib.Face):
    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)

        self.kbd = Keyboard(self.canvas)

        self.closeButton.onTap = self.onExit
        self.usernameFrame.onTap = self.onUsernameTap
        self.usernameText.onTap = self.onUsernameTap
        self.passwordFrame.onTap = self.onPasswordTap
        self.passwordText.onTap = self.onPasswordTap

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
        self.canvas.add(self.kbd)

    def onPasswordTap(self,e):
        self.kbd.resultProcessor = self.populatePassword
        self.canvas.add(self.kbd)
        
    def onLogin(self,e):
        self.twtApi = twitter.Api(username=self.username,password=self.password)
        self.resultProcessor(twitterApi)
       
    def onExit(self,e):
        inkface.exit()

class TwitGui(inklib.Face):
    twtApi = None

    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)

        self.twitButton.onTap = self.onTwit
        self.quitButton.onTap = self.onExit

        self.kbd = Keyboard(self.canvas)

        self.twtApi = twitter.Api(
                        username=os.environ['TWT_USERNAME'],
                        password=os.environ['TWT_PASSWORD'])

        ptwt_list = self.twtApi.GetPublicTimeline()

        i = 0
        LINE_LIMIT = 25 
        for name,elem in self.elements.items():
            j = 1
            twt_text = ''
            if name.startswith('publicTwt'):

                # Iterate till we get an ascii string
                while True:
                    try:
                        ascii_twt = str(ptwt_list[i].text)
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
        
def main():
    canvas = inkface.create_X_canvas()

    #twitGui = TwitGui(canvas,'twit.svg')
    #canvas.add(twitGui)

    loginGui = LoginGui(canvas,'login.svg')
    canvas.add(loginGui)

    canvas.eventloop()

if __name__ == '__main__':
    main()


