
from inkface.canvas import PygameFace, PygameCanvas
from twitter import twitter
import os
import pygame.image
import cairo
import array

class App:
    GAP = 7
    MAX_TWT_NUM = 7
    index = MAX_TWT_NUM 
    FRAMERATE = 20
    roll = []
    moveflag = False
    stopflag = False
    twtcnt = 0
    twtlist = None

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
        self.canvas = PygameCanvas((800,480),framerate=self.FRAMERATE)
        self.face = PygameFace('data/gui-6.svg')

        # Calculate some constants
        self.base_x = self.face.twt0.x
        self.base_y = self.face.twt0.y
        self.base_img_x = self.face.imgFrame0.x
        self.base_img_y = self.face.imgFrame0.y
        self.base_w = self.face.twt0.svg.w
        self.base_h = self.face.twt0.svg.h
        self.base_img_w = self.face.imgFrame0.svg.w
        self.base_img_h = self.face.imgFrame0.svg.h

        self.moveStep = self.base_h + self.GAP
        
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

        # Set the waitIcon to rotating effect
        self.face.waitIcon.onDraw = self.rotateIcon

        # Show the face on canvas
        self.canvas.add(self.face)

        for i in range(self.MAX_TWT_NUM + 1):
            elem = self.face.get('twt'+str(i))
            elem.onDraw = self.drawTwt
            twt = self.get_twt()

            elem.svg.text = twt.text
            elem.refresh(svg_reload=True)

            # render profile image
            eimg = self.face.get('imgFrame'+str(i))
            eimg.onDraw = self.drawTwt
            img = self.load_image(twt)
            iw = img.get_width()
            ih = img.get_height()
            eimg.sprite.image.blit(img,
                ((self.base_img_w - iw)/2,(self.base_img_h - ih)/2))

            self.roll.append((elem,eimg))

        self.roll[self.index][0].onDraw = self.processOffline
        self.roll[self.index][1].onDraw = self.processOffline
        
        self.face.nextButton.onLeftClick = self.rollToNext

        # waitIcon can disappear now
        self.face.waitIcon.onDraw = self.doNotDraw

        try:
            self.canvas.eventloop()
        except Exception, e:
            print 'Caught '+str(e)
            self.canvas.stop()
            self.stopflag = True

    def drawTwt(self, elem, screen):
        if self.moveflag:
            elem.y -= self.moveStep/self.FRAMERATE
            self.twtAnimCounter += 1

            if self.twtAnimCounter >= 2*self.MAX_TWT_NUM:
                self.twtAnimCounter = 0
                self.moveAmount -= int(self.moveStep/self.FRAMERATE)
                if self.moveAmount < int(self.moveStep/self.FRAMERATE):
                    self.moveflag = False

        screen.blit(elem.sprite.image,(elem.x,elem.y))

    def rotateIcon(self, elem, screen):
        #rot_icon = pygame.transform.rotate(elem.sprite.image,20.0)
        #screen.blit(rot_icon,(elem.x,elem.y))
        screen.blit(elem.sprite.image,(elem.x,elem.y))

    def doNotDraw(self, elem, screen):
        pass

    def processOffline(self, elem, screen):
        if self.moveflag:
            elem.y -= self.moveStep/self.FRAMERATE

    def load_image(self,twt):
        import urllib
        imgurl = twt.GetUser().profile_image_url
        print twt.GetUser().screen_name
        localfile = '/tmp/'+imgurl.split('/')[-1]
        try:
            urllib.urlretrieve(imgurl,localfile)
        except UnicodeError, ue:
            print 'Error fetching img URL'+str(ue)
            return None 
        image = pygame.image.load(localfile)
        return image
        
    def rollToNext(self):

        # incoming twit (invisible -> visible)
        incoming,incoming_img = self.roll[self.index]
        incoming.onDraw = self.drawTwt
        incoming_img.onDraw = self.drawTwt
        incoming.y = self.base_y + self.MAX_TWT_NUM*self.moveStep
        incoming_img.y = self.base_img_y + self.MAX_TWT_NUM*self.moveStep

        twt = self.get_twt()
        incoming.svg.text = twt.text
        incoming.refresh(svg_reload=True)

        img = self.load_image(twt)
        iw = img.get_width()
        ih = img.get_height()
        incoming_img.sprite.image.blit(img,
            ((self.base_img_w - iw)/2,(self.base_img_h - ih)/2))

        # index++
        self.index = (self.index + 1)%(self.MAX_TWT_NUM + 1)

        # outgoing twit (visible -> invisible)

        self.roll[self.index][0].onDraw = self.processOffline
        self.roll[self.index][1].onDraw = self.processOffline

        self.moveAmount = self.moveStep
        self.moveflag = True
        self.twtAnimCounter = 0


App().main()



