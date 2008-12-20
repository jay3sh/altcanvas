#!/usr/bin/python

import os
import re
import threading
import urllib2

import cairo

import inkface
import inklib
import twitter

from keyboard import Keyboard
from login import LoginGui
from imgloader import ImageLoader

import sys


class TwitGui(inklib.Face):
    twtApi = None
    PUBLIC_TIMELINE = 0
    FRIENDS_TIMELINE = 1

    public_cloud_pattern = 'publicCloud(\d+)'
    public_twt_pattern = 'publicTwt(\d+)'
    friend_cloud_pattern = 'friendCloud(\d+)'
    friend_twt_pattern = 'friendTwt(\d+)'
    friend_img_pattern = 'friendImg(\d+)'

    def __init__(self,canvas,svgname,api):
        inklib.Face.__init__(self,canvas,svgname)

        self.twitButton.onTap = self.onTwit
        self.quitButton.onTap = self.onExit

        self.kbd = Keyboard(self.canvas)

        self.twtApi = api

        for name,elem in self.elements.items():
            if name.startswith('publicTwt') or name.startswith('publicCloud'):
                elem.onTap = self.FocusPublicTwt
            elif name.startswith('friendTwt') or name.startswith('friendCloud'):
                elem.onTap = self.FocusFriendTwt
                elem.onMouseLeave = self.lostFocusTwt
            elif name.startswith('friendImg') or name.startswith('friendFrame'):
                elem.onDraw = self.donotdraw

        self.iloader = ImageLoader(None)
        self.iloader.start()

    def donotdraw(self,e):
        pass

    def drawProfileFrame(self,e):
        self.canvas.draw(e)

    def drawProfileImage(self,e):
        #print 'TG: drawProfileImage for '+e.name
        m = re.match(self.friend_img_pattern,e.name)
        if m:
            num = m.group(1)
            twt = self.elements['friendTwt'+str(num)].user_data

            if twt:
                url = twt.GetUser().profile_image_url
                #print 'TG: Getting cairo surface for '+url

                img_surface = e.user_data
                if not img_surface:
                    img_surface = self.iloader.get_image_surface(url)
                    e.user_data = img_surface

                if not img_surface:
                    return
                ctx = cairo.Context(e.surface)
                sx = e.surface.get_width()*1.0/img_surface.get_width()
                sy = e.surface.get_height()*1.0/img_surface.get_height()
                ctx.scale(sx,sy)
                ctx.set_source_surface(img_surface,0,0)
                ctx.paint()
                self.canvas.draw(e)
                self.canvas.refresh()
                #print 'TG: Drew the image'
        
    def lostFocusTwt(self,e):
        m = re.match(self.friend_cloud_pattern,e.name) or \
            re.match(self.friend_twt_pattern,e.name)
        if m:
            num = m.group(1)
            self.elements['friendImg'+str(num)].onDraw = self.donotdraw
            self.elements['friendFrame'+str(num)].onDraw = self.donotdraw
            self.canvas.refresh()

    def FocusFriendTwt(self,e):
        m = re.match(self.friend_cloud_pattern,e.name) or \
            re.match(self.friend_twt_pattern,e.name)
        if m:
            num = m.group(1)
            self.elements['friendImg'+str(num)].onDraw = self.drawProfileImage
            self.elements['friendFrame'+str(num)].onDraw = self.drawProfileFrame
            self.canvas.refresh()
            
    def FocusPublicTwt(self,e):
        m = re.match(self.public_cloud_pattern,e.name) or \
            re.match(self.public_twt_pattern,e.name)
        if m:
            num = m.group(1)
            #self.canvas.reset_order()
            #self.canvas.bring_to_front(self.elements['publicCloud'+str(num)])
            #self.canvas.bring_to_front(self.elements['publicTwt'+str(num)])
            #self.canvas.bring_to_front(self.twitButton)
            #self.canvas.bring_to_front(self.quitButton)
            #self.canvas.bring_to_front(self.friendsButton)
            #self.canvas.bring_to_front(self.publicButton)

    def loadTimeline(self,type):

        try:
            if type == self.PUBLIC_TIMELINE:
                LINE_LIMIT = 25 
                elem_prefix = 'publicTwt'
                twt_list = self.twtApi.GetPublicTimeline()
            else:
                LINE_LIMIT = 55 
                elem_prefix = 'friendTwt'
                twt_list = self.twtApi.GetFriendsTimeline()
        except urllib2.URLError, urle:
            print 'Error connecting to Twitter: '+str(urle)
            return

        i = 0
        image_list = []
        for name,elem in self.elements.items():
            j = 1
            twt_text = ''
            if name.startswith(elem_prefix):

                # Iterate till we get an ascii string
                while True:
                    try:
                        ascii_twt = str(twt_list[i].text)
                        elem.user_data = twt_list[i]
                        image_list.append(
                            twt_list[i].GetUser().profile_image_url)
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

        self.iloader.add_img_url(image_list)
        self.canvas.refresh()
        
    def onExit(self,e):
        self.iloader.stop = True
        print 'Waiting for imageLoader to stop'
        self.iloader.join()
        self.resultProcessor()

    def publishTwit(self,txt=None):
        if txt:
            #print dir(self.twtApi.PostUpdate(txt))
            print 'Pseudo publishing: '+txt
        self.canvas.remove(self.kbd)
        self.canvas.refresh()
        
    def onTwit(self,e):
        self.kbd.resultProcessor = self.publishTwit
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
        del self.loginGui

        self.twitGui = TwitGui(self.canvas,'public.svg',twitterApi)
        self.twitGui.resultProcessor = self.onExit
        self.canvas.add(self.twitGui)
        self.canvas.refresh()

        self.twitGui.loadTimeline(self.twitGui.FRIENDS_TIMELINE)
        self.twitGui.loadTimeline(self.twitGui.PUBLIC_TIMELINE)

    def onExit(self,user_data=None):
        #from time import sleep
        self.canvas.remove(self.twitGui)
        print 'twitGui refcount %d'%sys.getrefcount(self.twitGui)
        del self.twitGui
        #for i in range(10):
        #    print 'waiting %d'%i
        #    sleep(1)
        #inkface.exit()


if __name__ == '__main__':
    TwitterApp().main()


