#!/usr/bin/env python

import sys
import thread
import time
import gtk
from gtk import keysyms
import os
import cairo
import libpub

from libpub.prime.widgets.image import Image
from libpub.prime.widgets.label import Label 
from libpub.prime.widgets.entry import Entry 
from libpub.prime.widgets.fancyentry import FancyEntry 

import libpub.prime.mask as mask

from libpub.prime.app import PublishrApp

from libpub.prime.utils import get_image_locations,\
    LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD,detect_platform,log


        
if detect_platform() == 'Nokia':
    from hildon import Window as BaseWindow
else:
    from gtk import Window as BaseWindow
    

class Canvas(BaseWindow):
    key_listeners = []
    pointer_listeners = []
    appQ = []
    da = None
    gc = None
    lastx = 0
    lasty = 0
    curx = 0
    cury = 0
    pressed = False
    isLoaded = False
    
    __ignore_pointer_count = 0
    
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 480
    
    def __init__(self):
        BaseWindow.__init__(self)
        
        if detect_platform() == 'Nokia':
            self.fullscreen()
            
        self.connect("destroy", gtk.main_quit)
        self.connect('key-press-event',self.key_handler)
        self.set_default_size(self.CANVAS_WIDTH,self.CANVAS_HEIGHT)
        
        self.da = gtk.DrawingArea()
        
        self.da.connect('expose_event',self.expose)
        self.da.connect('configure_event',self.configure)
        self.da.connect('button_press_event',self.button_press)
        self.da.connect('button_release_event',self.button_release)
        self.da.connect('motion_notify_event',self.motion_notify)

        self.da.set_events(gtk.gdk.EXPOSURE_MASK
                       | gtk.gdk.LEAVE_NOTIFY_MASK
                       | gtk.gdk.BUTTON_PRESS_MASK
                       | gtk.gdk.BUTTON_RELEASE_MASK
                       | gtk.gdk.POINTER_MOTION_MASK
                       | gtk.gdk.POINTER_MOTION_HINT_MASK)
    
        self.add(self.da)
        self.show_all()
        
    def load(self):
        if self.isLoaded:
            return
        
        if detect_platform() == 'Nokia':
            app = PublishrApp('/mnt/bluebox/photos')
        else:
            app = PublishrApp('/photos/altimages/jyro')
            
        #app.register_change_listener(self.on_app_change)
        self.appQ.append((app,0,0))
        self.isLoaded = True
        
    '''
    def on_app_change(self,app):
        # In future we will use app's params to decide if we want
        # to update or not
        self.redraw()
        self.da.window.draw_drawable(self.gc, self.pixmap, 0,0, 0,0, -1,-1)
    '''
        
    def __redraw(self):
        self.ctx.rectangle(0,0,self.CANVAS_WIDTH,self.CANVAS_HEIGHT)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.fill()
        for app in self.appQ:
            #app_surface = app[0].get_surface()
            app[0].redraw()
            app_surface = app[0].surface
            self.ctx.set_source_surface(app_surface,app[1],app[2])
            self.ctx.paint()
            
        
    def configure(self,widget,event):
        _,_,w,h = widget.allocation
        self.pixmap = gtk.gdk.Pixmap(widget.window,w,h)
        w,h = self.pixmap.get_size()
        self.ctx = self.pixmap.cairo_create()
        self.ctx.set_source_rgb(1,1,1)
        self.ctx.rectangle(0,0,w,h)
        self.ctx.fill()
        
        # triggers expose event
        widget.queue_draw()
    
    def expose(self,widget,event):
        # redraw the drawing area
        self.__redraw()
        
        if not self.gc:
            self.gc = gtk.gdk.GC(widget.window)
        widget.window.draw_drawable(self.gc, self.pixmap, 0,0, 0,0, -1,-1)
        
    def redraw(self):
        self.expose(self.da, None)
        
    def key_handler(self,window,event):
        keyval = event.keyval
        state = event.state & gtk.accelerator_get_default_mod_mask()
        for app in self.appQ:
            app[0].dispatch_key_event(keyval,state)
        
    def button_press(self,widget,event):
        self.pressed = True

    def button_release(self,widget,event):
        self.pressed = False

    def motion_notify(self,widget,event):
        if event.is_hint:
            x,y,state = event.window.get_pointer()
        else:
            x = event.x
            y = event.y
            state = event.state
        
        self.__ignore_pointer_count += 1
        self.__ignore_pointer_count %= 3
        
        if self.__ignore_pointer_count == 0:
            for app in self.appQ:
        	   app[0].dispatch_pointer_event(x,y,self.pressed)
        
        widget.queue_draw()


    def run(self):
        self.load()
        gtk.main()


if __name__ == '__main__':
    canvas = Canvas()
    libpub.prime.canvas = canvas
    canvas.run()