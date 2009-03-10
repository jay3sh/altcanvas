
import pygame
from twtinklib import twitter

class Twt:
    (TWT_FRIENDS, TWT_PUBLIC, TWT_REPLIES) = range(3)
    def __init__(self, username, password, face, canvas):
        self.face = face
        self.canvas = canvas
        self.twtApi = twitter.Api(username, password)

        self.friends_page_num = 1
        self.replies_page_num = 1

        self.friends_twtlist = \
            self.twtApi.GetFriendsTimeline(page=self.friends_page_num)
        self.public_twtlist = None
        self.replies_twtlist = None

        self.friends_page_num += 1

        self.friends_twtcnt = 0
        self.public_twtcnt = 0
        self.replies_twtcnt = 0
        self.GAP = 10
        self.FRAMERATE = 12 
        self.roll = []
        self.moveflag = False
        self.stopflag = False
        self.rotation = 0.0
        self.width = int(float(self.face.svg.width))
        self.height = int(float(self.face.svg.height))

        self.base_x,self.base_y = self.face.twt0.get_position()
        self.base_img_x,self.base_img_y = self.face.imgFrame0.get_position()
        self.base_w = self.face.twt0.svg.w
        self.base_h = self.face.twt0.svg.h
        self.base_img_w = self.face.imgFrame0.svg.w
        self.base_img_h = self.face.imgFrame0.svg.h

        self.moveStep = self.base_h + self.GAP
        
        self.MAX_TWT_NUM = (self.height / self.moveStep) + 1
 
    def get_public_twt(self):
        if self.public_twtlist == None or \
            self.public_twtcnt >= len(self.public_twtlist):
            
            self.public_twtlist = \
                self.twtApi.GetPublicTimeline()
            self.public_twtcnt = 0
        twt = self.public_twtlist[self.public_twtcnt]
        self.public_twtcnt += 1
        return twt

    def get_replies(self):
        if self.replies_twtlist == None or \
            self.replies_twtcnt >= len(self.replies_twtlist):
            
            self.replies_twtlist = \
                    self.twtApi.GetReplies(page=self.replies_page_num)
            self.replies_page_num += 1
            self.replies_twtcnt = 0
        twt = self.replies_twtlist[self.replies_twtcnt]
        self.replies_twtcnt += 1
        return twt

    def get_friends_twt(self):
        if self.friends_twtcnt >= len(self.friends_twtlist):
            self.friends_twtlist = \
                self.twtApi.GetFriendsTimeline(page=self.friends_page_num)
            self.friends_page_num += 1
            self.friends_twtcnt = 0
        twt = self.friends_twtlist[self.friends_twtcnt]
        self.friends_twtcnt += 1
        return twt

    def reset_twt_roll(self):
        # Make all the twits and imageFrames invisible to start with
        for i in range(self.MAX_TWT_NUM + 1):
            self.face.get('twt'+str(i)).hide()
            self.face.get('imgFrame'+str(i)).hide()
        self.face.nextButton.hide()
        self.canvas.update()

    def load_twts(self, twt_type=TWT_FRIENDS):
        self.get_twt = {
            self.TWT_FRIENDS    : self.get_friends_twt,
            self.TWT_PUBLIC     : self.get_public_twt,
            self.TWT_REPLIES    : self.get_replies
        }[twt_type]

        for i in range(self.MAX_TWT_NUM + 1):
            elem = self.face.get('twt'+str(i))

            twt = self.get_twt()

            print twt.text
            elem.svg.text = twt.text
            elem.refresh(svg_reload=True)

            # render profile image
            eimg = self.face.get('imgFrame'+str(i))
            img = self.load_image(twt)
            if img == None: continue
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
 
    def load(self):
        self.index = self.MAX_TWT_NUM 


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

        self.reset_twt_roll()

        # Set visibility of button borders
        self.face.friendsBorder.unhide()
        self.face.everyoneBorder.hide()
        self.face.repliesBorder.hide()
        self.face.twitBorder.hide()

        self.face.everyoneButton.onLeftClick = self.onEveryoneClicked

        # Set the waitIcon to rotating effect
        self.face.waitIcon.unhide()

        # Show the face on canvas
        self.canvas.add(self.face)

        self.load_twts()
       
        self.face.nextButton.onLeftClick = self.rollToNext

        self.face.nextButton.unhide()

        # waitIcon can disappear now
        self.face.waitIcon.hide()

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
        image = pygame.image.load(localfile)
        return image
        
    def onEveryoneClicked(self, elem):
        print 'loading public timeline'
        self.reset_twt_roll()

        # Set the waitIcon to rotating effect
        self.face.waitIcon.unhide()

        self.load_twts(twt_type=self.TWT_PUBLIC)

        self.face.nextButton.unhide()

    def onRepliesClick(self, elem):
        pass

    def onFriendsClick(self, elem):
        pass

    def onTwitClick(self, elem):
        pass

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



 




