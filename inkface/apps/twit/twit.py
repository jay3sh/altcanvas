#!/usr/bin/python

import inkface
import inklib
import twitter
from keyboard import Keyboard

import os

class TwitGui(inklib.Face):
    twtApi = None

    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)

        self.twitButton.onTap = self.onTwit
        self.quitButton.onTap = self.onExit

        '''
        self.kbd = Keyboard(self.canvas)
        self.kbd.visible = False

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
        '''

    def onExit(self,e,elements):
        inkface.exit()

    def onTwit(self,e,elements):
        self.kbd.visible = True
        self.canvas.refresh()
        
def main():
    canvas = inkface.create_X_canvas()
    twitGui = TwitGui(canvas,'twit.svg')
    canvas.add(twitGui)

    canvas.eventloop()

if __name__ == '__main__':
    main()


