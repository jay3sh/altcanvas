import gtk
from gtk import keysyms
import os
import cairo

from libpub.prime.widgets.image import Image
from libpub.prime.widgets.label import Label 
from libpub.prime.widgets.entry import Entry 

import libpub.prime.mask as mask

from libpub.prime.utils import get_image_locations,LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD

FOLDER_PATH='/photos/altimages/jyro'

    
def load_widgets(pixmap,app):
    w,h = pixmap.get_size()
    ctx = pixmap.cairo_create()
    
    x = 0
    y = 0
    lbl = Label('Brewing cup of coffee...')
    ctx.set_source_surface(lbl.surface,x,y)
    ctx.paint()
    
    x = 0
    y = 100
    entry = Entry(parent=app,size=15)
    app.register_keylistener(entry)
    ctx.set_source_surface(entry.get_surface(),x,y)
    ctx.paint()

def load_images(pixmap):
    images = []
    if os.path.isdir(FOLDER_PATH):
        files = os.listdir(FOLDER_PATH)
        for f in files:
            if f.lower().endswith('jpg') or  \
                f.lower().endswith('jpeg') or  \
                f.lower().endswith('xcf') or  \
                f.lower().endswith('gif'):
                    images.append(FOLDER_PATH+os.sep+f)
    
    w,h = pixmap.get_size()
    ctx = pixmap.cairo_create()
    #gradient = mask.Linear(100,100).surface
    gradient = mask.Radial(100,100).surface
    
    i = 0
    for (x,y) in get_image_locations(
            len(images),layout=LAYOUT_UNIFORM_SPREAD):
        img = Image(images[i],100,100)
        ctx.set_source_surface(img.surface,x,y)
        ctx.mask_surface(gradient,x,y)
        i = i+1
                    
class App(gtk.Window):
    key_listeners = []
    widgetQ = []
    da = None
    lastx = 0
    lasty = 0
    curx = 0
    cury = 0
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", gtk.main_quit)
        self.connect('key-press-event',self.key_handler)
        self.set_default_size(800,480)
        
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
        entry1 = Entry(parent=self.da,x=100,y=100,size=10)
        self.widgetQ.append(entry1)
        self.register_keylistener(entry1)
        entry2 = Entry(parent=self.da,x=100,y=200,size=10)
        self.widgetQ.append(entry2)
        self.register_keylistener(entry2)
        
        
    def redraw(self):
        for widget in self.widgetQ:
            self.ctx.set_source_surface(widget.get_surface(),widget.x,widget.y)
            self.ctx.paint()
        
    def configure(self,widget,event):
        _,_,w,h = widget.allocation
        self.pixmap = gtk.gdk.Pixmap(widget.window,w,h)
        w,h = self.pixmap.get_size()
        self.ctx = self.pixmap.cairo_create()
        self.ctx.set_source_rgb(1,1,1)
        self.ctx.rectangle(0,0,w,h)
        self.ctx.fill()
        
        # Load initial set of widgets
        self.load()
        
        # triggers expose event
        widget.queue_draw()
    
    def expose(self,widget,event):
        
        # redraw the drawing area
        self.redraw()
        
        gc = gtk.gdk.GC(widget.window)
        widget.window.draw_drawable(gc, self.pixmap, 0,0, 0,0, -1,-1)
        
    def key_handler(self,window,event):
        keyval = event.keyval
        state = event.state & gtk.accelerator_get_default_mod_mask()
        
        for keyl in self.key_listeners:
            keyl(keyval,state)
            
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
        # Save current x,y info into last x,y info and
        # update the current x,y info with incoming pointer location
        # Finally trigger expose event for refresh
        self.lastx = self.curx
        self.lasty = self.cury
        self.curx = x
        self.cury = y
        print "%d, %d --> %d, %d"%(self.lastx,self.lasty,self.curx,self.cury)
        widget.queue_draw()

            
    def register_keylistener(self,key_listener_obj):
        if not hasattr(key_listener_obj,'key_listener'):
            raise Exception('Invalid key listener')
        
        self.key_listeners.append(key_listener_obj.key_listener)

    def run(self):
        gtk.main()


if __name__ == '__main__':
    App().run()