
import os
import sys
from etwtlib import twitter
from etwtlib.textbox import TextBox
from etwtlib.twitbox import TwitBox
from etwtlib.container import Container
from etwtlib.imgthread import ImageThread

from inkface.evas import EFace, ECanvas


PREFIX      = '..'
SVG_DIR     = os.path.join(PREFIX,'svg')

IMAGE_CACHE_DIR = os.path.join(os.path.sep+'tmp','.twitinkimg')

class Twt:
    (TWT_FRIENDS, TWT_PUBLIC, TWT_REPLIES, TWT_TWIT) = range(4)
    def __init__(self, username, password, theme, canvas, twt_type=TWT_FRIENDS):
        self.canvas = canvas
        self.twtApi = twitter.Api(username, password)

        self.current_twt_type = twt_type

        self.face = EFace(
            os.path.join(SVG_DIR, theme, 'twits.svg'), self.canvas)

        self.friends_page_num = 1
        self.replies_page_num = 1

        self.friends_twtlist = None
        self.public_twtlist = None
        self.replies_twtlist = None

        self.friends_twtcnt = 0
        self.public_twtcnt = 0
        self.replies_twtcnt = 0

        self.image_thread = ImageThread()
        self.image_thread.start()
 
    def get_public_twt(self):
        if self.public_twtlist is None or \
            self.public_twtcnt >= len(self.public_twtlist):
            
            self.public_twtlist = \
                self.twtApi.GetPublicTimeline()
            self.public_twtcnt = 0
        twt = self.public_twtlist[self.public_twtcnt]
        self.public_twtcnt += 1
        return twt

    def get_replies(self):
        if self.replies_twtlist is None or \
            self.replies_twtcnt >= len(self.replies_twtlist):
            
            self.replies_twtlist = \
                    self.twtApi.GetReplies(page=self.replies_page_num)
            self.replies_page_num += 1
            self.replies_twtcnt = 0
        twt = self.replies_twtlist[self.replies_twtcnt]
        self.replies_twtcnt += 1
        return twt

    def get_friends_twt(self):
        if self.friends_twtlist is None or \
            self.friends_twtcnt >= len(self.friends_twtlist):

            self.friends_twtlist = \
                self.twtApi.GetFriendsTimeline(page=self.friends_page_num)
            self.friends_page_num += 1
            self.friends_twtcnt = 0
        twt = self.friends_twtlist[self.friends_twtcnt]
        self.friends_twtcnt += 1
        return twt

    def onTwtboxChange(self, text):
        self.face.update_counter.svg.text = str(len(text))
        self.face.update_counter.refresh(svg_reload=True)

    def load(self):

        self.face.closeButton.onLeftClick = self.exit

        self.face.waitIcon.unhide()

        # Show the face on canvas
        self.canvas.add(self.face)

        # Create a container box
        container_bbox = (0, 0, self.face.svg.width, self.face.svg.height)

        self.twtContainer = Container(
                        bbox            = container_bbox,
                        upArrow_elem    = self.face.upArrow,
                        downArrow_elem  = self.face.downArrow)

        self.twtContainer.connect('request',self.add_new_tbox)

        self.load_twts(self.current_twt_type)

        self.face.upArrow.refresh(svg_reload=False)
        self.face.downArrow.refresh(svg_reload=False)

        # waitIcon can disappear now
        self.face.waitIcon.hide()

    def load_twts(self, twt_type):
        self.get_twt = \
                {
                    self.TWT_FRIENDS    : self.get_friends_twt,
                    self.TWT_PUBLIC     : self.get_public_twt,
                    self.TWT_REPLIES    : self.get_replies
                }[twt_type]

        tboxes = self.twtContainer.get_widgets()

        twt = self.get_twt()

        self.tbox = TwitBox(
            self.face,
            background_ename = 'twtbg',
            text_ename       = 'twttxt',
            image_ename      = 'twtimg')

        self.add_new_tbox(None, self.tbox)

    def add_new_tbox(self, position, tbox=None):
        containerFull = False
        while not containerFull:
            twt = self.get_twt()
            if tbox is None:
                tbox = self.tbox.clone(position)
            tbox.set_text(twt.text)
            self.image_thread.add_work(
                (twt.GetUser().profile_image_url,tbox.image_elem))

            lx,ly,lw,lh = tbox.get_bounding_box()
            position = (lx, ly+lh+4)

            containerFull = self.twtContainer.add(tbox)
            tbox = None

    def change_borders(self, type):
        for t, border in self.button_borders.items():
            if t == type:
                border.unhide()
            else:
                border.hide()
 
    def onEveryoneClicked(self, elem):
        if self.current_twt_type == self.TWT_PUBLIC:
            return

        #self.reset_twt_roll()

        self.change_borders(self.TWT_PUBLIC)
        self.face.waitIcon.unhide()

        self.load_twts(twt_type=self.TWT_PUBLIC)

        self.face.waitIcon.hide()

        self.current_twt_type = self.TWT_PUBLIC

    def onRepliesClicked(self, elem):
        if self.current_twt_type == self.TWT_REPLIES:
            return

        #self.reset_twt_roll()

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

        self.unhide_twt_entry()

        self.current_twt_type = self.TWT_TWIT

    def onTwitPost(self, elem):
        #self.twtApi.PostUpdate(self.twtentry.get_text())
        print self.twtentry.get_text()
        self.hide_twt_entry()

    def onTwitCancel(self,elem):
        self.hide_twt_entry()

    def exit(self, elem):
        self.image_thread.stop()
        self.image_thread.join()
        self.canvas.stop()
