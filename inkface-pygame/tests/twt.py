
from inkface.canvas import PygameFace, PygameCanvas
from twitter import twitter
import os

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

        self.base_x = self.face.twt0.x
        self.base_img_x = self.face.img0.x
        self.base_y = self.face.twt0.y
        self.base_img_y = self.face.img0.y
        self.base_w = self.face.twt0.svg.w
        self.base_h = self.face.twt0.svg.h

        self.moveStep = self.base_h + self.GAP
        
        for i in range(self.MAX_TWT_NUM):
            self.face.clone('twt0','twt'+str(i+1),
                            new_x = self.base_x,
                            new_y = self.base_y+\
                                ((i+1)*(self.base_h + self.GAP)))
            self.face.clone('img0','img'+str(i+1),
                            new_x = self.base_img_x,
                            new_y = self.base_img_y+\
                                ((i+1)*(self.base_h + self.GAP)))

        for i in range(self.MAX_TWT_NUM + 1):
            elem = self.face.get('twt'+str(i))
            eimg = self.face.get('img'+str(i))
            elem.onDraw = self.drawTwt
            twt = self.get_twt()
            img = self.load_image(twt)

            eimg.sprite.image.blit(img,(0,0))
            elem.svg.text = twt.text
            elem.refresh(svg_reload=True)
            self.roll.append(elem)

        self.roll[self.index].onDraw = self.doNotDraw
        
        self.face.nextButton.onLeftClick = self.rollToNext

        self.canvas.add(self.face)
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

            if self.twtAnimCounter >= self.MAX_TWT_NUM:
                self.twtAnimCounter = 0
                self.moveAmount -= int(self.moveStep/self.FRAMERATE)
                if self.moveAmount < int(self.moveStep/self.FRAMERATE):
                    self.moveflag = False

        screen.blit(elem.sprite.image,(elem.x,elem.y))

    def doNotDraw(self, elem, screen):
        if self.moveflag:
            elem.y -= self.moveStep/self.FRAMERATE

    def normalize(self, text):
        LINE_LIMIT = 10 
        j = 0
        new_text = ''
        for c in text:
            if c == '\n':
                j += 1
                continue
            if j%LINE_LIMIT == 0:
                new_text += '\n'+c
            else:
                new_text += c
            j += 1
        return new_text

    def load_image(self,twt):
        import urllib
        import pygame.image
        imgurl = twt.GetUser().profile_image_url
        localfile = '/tmp/'+imgurl.split('/')[-1]
        try:
            urllib.urlretrieve(imgurl,localfile)
        except UnicodeError, ue:
            print 'Error fetching img URL'+str(ue)
            return None 
        image = pygame.image.load(localfile)
        return image
        
    def rollToNext(self):
        incoming = self.roll[self.index]
        incoming.onDraw = self.drawTwt
        incoming.y = self.base_x + self.MAX_TWT_NUM*self.moveStep
        twt = self.get_twt()
        #img = self.load_image(twt)
        incoming.svg.text = twt.text
        incoming.refresh(svg_reload=True)

        self.index = (self.index + 1)%(self.MAX_TWT_NUM + 1)

        self.roll[self.index].onDraw = self.doNotDraw

        self.moveAmount = self.moveStep
        self.moveflag = True
        self.twtAnimCounter = 0


App().main()



