
from inkface.canvas.pygamecanvas import PygameFace, PygameCanvas
from twitter import twitter
import os
import sys
import pygame.image
import cairo
import array

class App:
    GAP = 2
    FRAMERATE = 12 
    roll = []
    moveflag = False
    stopflag = False
    twtcnt = 0
    twtlist = None
    rotation = 0.0

    def __init__(self):
        self.twtApi = twitter.Api(
                username=os.environ['TWT_USERNAME'],
                password=os.environ['TWT_PASSWORD'])
        self.twtlist = self.twtApi.GetFriendsTimeline()

    def get_twt(self):
        if self.twtcnt >= len(self.twtlist):
            self.twtlist = self.twtApi.GetFriendsTimeline()
            self.twtcnt = 0
        twt = self.twtlist[self.twtcnt]
        self.twtcnt += 1
        return twt

    def main(self):
        self.face = PygameFace(sys.argv[1])

        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
 
        self.width = int(float(self.face.svg.width))
        self.height = int(float(self.face.svg.height))
        self.canvas = PygameCanvas(
            (self.width,self.height),
            framerate=self.FRAMERATE, flags=flags)
        # Calculate some constants
        self.base_x,self.base_y = self.face.twt0.get_position()
        self.base_img_x,self.base_img_y = self.face.imgFrame0.get_position()
        self.base_w = self.face.twt0.svg.w
        self.base_h = self.face.twt0.svg.h
        self.base_img_w = self.face.imgFrame0.svg.w
        self.base_img_h = self.face.imgFrame0.svg.h

        self.moveStep = self.base_h + self.GAP
        
        self.MAX_TWT_NUM = (self.height / self.moveStep) + 1
        self.index = self.MAX_TWT_NUM 

        print 'step: %d'%(self.moveStep)
        # Clone elements
        for i in range(self.MAX_TWT_NUM):
            self.face.clone('twt0','twt'+str(i+1),
                            new_x = self.base_x,
                            new_y = self.base_y+\
                                ((i+1)*(self.base_h + self.GAP)))
            self.face.clone('imgFrame0','imgFrame'+str(i+1),
                            new_x = self.base_img_x,
                            new_y = self.base_img_y+\
                                ((i+1)*(self.base_h + self.GAP)))

        # Make all the twits and imageFrames invisible to start with
        for i in range(self.MAX_TWT_NUM + 1):
            self.face.get('twt'+str(i)).hide()
            self.face.get('imgFrame'+str(i)).hide()
        self.face.nextButton.hide()

        # Set the waitIcon to rotating effect
        self.face.waitIcon.unhide()

        # Show the face on canvas
        self.canvas.add(self.face)

        for i in range(self.MAX_TWT_NUM + 1):
            elem = self.face.get('twt'+str(i))
            twt = self.get_twt()

            elem.svg.text = twt.text
            elem.refresh(svg_reload=True)

            # render profile image
            eimg = self.face.get('imgFrame'+str(i))
            img = self.load_image(twt)
            if img is not None:
                iw = img.get_width()
                ih = img.get_height()
                eimg.sprite.image.blit(img,
                    ((self.base_img_w - iw)/2,(self.base_img_h - ih)/2))

            # Now the twit and image are ready to show
            elem.onDraw = self.drawTwt
            eimg.onDraw = self.drawTwt

            self.roll.append((elem,eimg))

        self.roll[self.index][0].onDraw = self.processOffline
        self.roll[self.index][1].onDraw = self.processOffline
        
        self.face.nextButton.onLeftClick = self.rollToNext

        self.face.nextButton.unhide()

        # waitIcon can disappear now
        self.face.waitIcon.hide()

        print 'step decrement = %f'%(self.moveStep/self.FRAMERATE)
        print 'rollOver adj. = %f'%(self.base_y + self.MAX_TWT_NUM*self.moveStep)
        try:
            self.canvas.eventloop()
        except Exception, e:
            print 'Caught '+str(e)
            self.canvas.stop()
            self.stopflag = True

    def drawTwt(self, elem):
        elem.unhide()
        if self.moveflag:
            elem_x, elem_y = elem.get_position()
            elem_y -= self.moveStep/self.FRAMERATE
            elem.set_position((elem_x, elem_y))
            self.twtAnimCounter += 1

            if self.twtAnimCounter >= 2*self.MAX_TWT_NUM:
                self.twtAnimCounter = 0
                self.moveAmount -= int(self.moveStep/self.FRAMERATE)
                if self.moveAmount < int(self.moveStep/self.FRAMERATE):
                    self.moveflag = False

    def processOffline(self, elem):
        if self.moveflag:
            elem_x, elem_y = elem.get_position()
            elem_y -= self.moveStep/self.FRAMERATE
            elem.set_position((elem_x,elem_y))

    def load_image(self,twt):
        import urllib
        imgurl = twt.GetUser().profile_image_url
        localfile = '/tmp/'+imgurl.split('/')[-1]
        try:
            urllib.urlretrieve(imgurl,localfile)
        except UnicodeError, ue:
            print 'Error fetching img URL'+str(ue)
            return None 
        try:
            image = pygame.image.load(localfile)
        except Exception, e:
            print 'Error loading '+localfile+': '+str(e)
            return None

        return image
        
    def rollToNext(self, elem):

        self.face.waitIcon.unhide()

        # incoming twit (invisible to visible)
        incoming,incoming_img = self.roll[self.index]
        incoming.onDraw = self.drawTwt
        incoming_img.onDraw = self.drawTwt
        incoming.unhide()
        incoming_img.unhide()

        incoming_x, incoming_y = incoming.get_position()
        incoming_y = self.base_y + self.MAX_TWT_NUM*self.moveStep
        incoming.set_position((incoming_x, incoming_y))

        incoming_img_x, incoming_img_y = incoming_img.get_position()
        incoming_img_y = self.base_img_y + self.MAX_TWT_NUM*self.moveStep
        incoming_img.set_position((incoming_img_x,incoming_img_y))

        twt = self.get_twt()
        incoming.svg.text = twt.text
        incoming.refresh(svg_reload=True)

        img = self.load_image(twt)
        iw = img.get_width()
        ih = img.get_height()
        incoming_img.sprite.image.blit(img,
            ((self.base_img_w - iw)/2,(self.base_img_h - ih)/2))

        # Increment Index
        self.index = (self.index + 1)%(self.MAX_TWT_NUM + 1)

        # outgoing twit (visible to invisible)
        self.roll[self.index][0].hide()
        self.roll[self.index][1].hide()

        self.roll[self.index][0].onDraw = self.processOffline
        self.roll[self.index][1].onDraw = self.processOffline

        self.moveAmount = self.moveStep
        self.moveflag = True
        self.twtAnimCounter = 0
        self.face.waitIcon.hide()

App().main()



