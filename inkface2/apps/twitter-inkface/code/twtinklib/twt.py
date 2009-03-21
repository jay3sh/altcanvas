
import os
import pygame
import sys
from twtinklib import twitter
from twtinklib.textbox import TextBox
from twtinklib.twitbox import TwitBox
from inkface.canvas.pygamecanvas import PygameFace, PygameCanvas

PREFIX      = '..'
SVG_DIR     = os.path.join(PREFIX,'svg')

IMAGE_CACHE_DIR = os.path.join(os.path.sep+'tmp','.twitinkimg')

class Twt:
    (TWT_FRIENDS, TWT_PUBLIC, TWT_REPLIES, TWT_TWIT) = range(4)
    def __init__(self, username, password, theme, canvas):
        self.canvas = canvas
        self.twtApi = twitter.Api(username, password)

        self.face = PygameFace(
            os.path.join(SVG_DIR, theme, 'twits.svg'))

        self.friends_page_num = 1
        self.replies_page_num = 1

        self.friends_twtlist = \
            self.twtApi.GetFriendsTimeline(page=self.friends_page_num)
        self.public_twtlist = None
        self.replies_twtlist = None

        self.friends_page_num += 1
        self.current_twt_type = self.TWT_FRIENDS

        self.friends_twtcnt = 0
        '''
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
        '''
 
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

    def hide_twt_box(self):
        for elem in (self.face.update_border,
                    self.face.update_txt,
                    self.face.update_cursor,
                    self.face.update_background,
                    self.face.postButton,
                    self.face.cancelButton,
                    self.face.update_counter):
            elem.hide()

    def unhide_twt_box(self):
        for elem in (self.face.update_border,
                    self.face.update_txt,
                    self.face.update_cursor,
                    self.face.update_background,
                    self.face.postButton,
                    self.face.cancelButton,
                    self.face.update_counter):
            elem.unhide()

    def onTwtboxChange(self, text):
        self.face.update_counter.svg.text = str(len(text))
        self.face.update_counter.refresh(svg_reload=True)

    def prepare_twt_box(self):
        self.twtbox = TextBox(
                            border_elem = self.face.update_border,
                            txt_elem    = self.face.update_txt,
                            cursor_elem = self.face.update_cursor,
                            framerate   = self.canvas.framerate)

        self.twtbox.register_change_listener(self.onTwtboxChange)

        self.face.postButton.onLeftClick = self.onTwitPost
        self.face.cancelButton.onLeftClick = self.onTwitCancel
 
    def load(self):

        self.prepare_twt_box()

        self.hide_twt_box()

        self.face.closeButton.onLeftClick = self.exit

        # Setup top buttons and their borders
        self.button_borders = \
                {
                    self.TWT_FRIENDS    : self.face.friendsBorder,
                    self.TWT_PUBLIC     : self.face.everyoneBorder,
                    self.TWT_REPLIES    : self.face.repliesBorder,
                    self.TWT_TWIT       : self.face.twitBorder
                }

        self.change_borders(self.TWT_FRIENDS)

        self.face.everyoneButton.onLeftClick = self.onEveryoneClicked
        self.face.repliesButton.onLeftClick = self.onRepliesClicked
        self.face.friendsButton.onLeftClick = self.onFriendsClicked
        self.face.twitButton.onLeftClick = self.onTwitClicked

        self.face.waitIcon.unhide()


        # Show the face on canvas
        self.canvas.add(self.face)

        tboxlist = []

        twt = self.get_friends_twt()

        tbox = TwitBox(
            self.face,
            background_ename = 'twtbg',
            text_ename       = 'twttxt',
            image_ename      = 'twtimg')
        
        tbox.set_text(twt.text)
        tbox.set_image(self.load_image(twt))

        lx,ly,lw,lh = tbox.get_bounding_box()

        for i in range(8):

            twt = self.get_friends_twt()

            new_tbox = tbox.clone((lx, ly+lh+4))

            new_tbox.set_text(twt.text)

            new_tbox.set_image(self.load_image(twt))

            lx,ly,lw,lh = new_tbox.get_bounding_box()


        # waitIcon can disappear now
        self.face.waitIcon.hide()

    def on_gain_focus(self, elem):
        elem.inFocus = True

    def on_lose_focus(self, elem):
        elem.inFocus = False


    def change_borders(self, type):
        for t, border in self.button_borders.items():
            if t == type:
                border.unhide()
            else:
                border.hide()
 
    def load_image(self,twt):
        import urllib
        if not os.path.exists(IMAGE_CACHE_DIR):
            os.makedirs(IMAGE_CACHE_DIR)
        imgurl = twt.GetUser().profile_image_url
        localfile = os.path.join(IMAGE_CACHE_DIR,imgurl.split('/')[-1])

        if not os.path.exists(localfile):
            try:
                urllib.urlretrieve(imgurl,localfile)
            except UnicodeError, ue:
                print 'Error fetching img URL'+str(ue)
                return None 
            except IOError, ioe:
                print 'IOError fetching img: '+str(ioe)
                return None
 
        image = pygame.image.load(localfile)
        return image
        
    def onEveryoneClicked(self, elem):
        if self.current_twt_type == self.TWT_PUBLIC:
            return

        self.reset_twt_roll()

        self.change_borders(self.TWT_PUBLIC)
        self.face.waitIcon.unhide()

        self.load_twts(twt_type=self.TWT_PUBLIC)

        self.face.waitIcon.hide()

        self.current_twt_type = self.TWT_PUBLIC

    def onRepliesClicked(self, elem):
        if self.current_twt_type == self.TWT_REPLIES:
            return

        self.reset_twt_roll()

        self.change_borders(self.TWT_REPLIES)
        self.face.waitIcon.unhide()

        self.load_twts(twt_type=self.TWT_REPLIES)

        self.face.waitIcon.hide()

        self.current_twt_type = self.TWT_REPLIES

    def onFriendsClicked(self, elem):
        if self.current_twt_type == self.TWT_FRIENDS:
            return
        self.reset_twt_roll()

        self.change_borders(self.TWT_FRIENDS)
        self.face.waitIcon.unhide()

        self.load_twts(twt_type=self.TWT_FRIENDS)

        self.face.waitIcon.hide()

        self.current_twt_type = self.TWT_FRIENDS

    def onTwitClicked(self, elem):
        if self.current_twt_type == self.TWT_TWIT:
            return

        self.change_borders(self.TWT_TWIT)

        self.unhide_twt_box()

        self.current_twt_type = self.TWT_TWIT

    def onTwitPost(self, elem):
        self.twtApi.PostUpdate(self.twtbox.get_text())
        #print self.twtbox.get_text()
        self.hide_twt_box()

    def onTwitCancel(self,elem):
        self.hide_twt_box()


    def exit(self, elem):
        self.canvas.stop()
        sys.exit(0)
