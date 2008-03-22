import gtk
from gtk import keysyms
import os
import cairo

from libpub.prime.widgets.image import Image
from libpub.prime.utils import get_image_locations,LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD
import libpub.prime.mask as mask

FOLDER_PATH='/photos/altimages/jyro'


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
    gradient = mask.Linear(100,100).surface
    
    i = 0
    for (x,y) in get_image_locations(
            len(images),layout=LAYOUT_UNIFORM_SPREAD):
        img = Image(images[i],100,100)
        ctx.set_source_surface(img.surface,x,y)
        ctx.mask_surface(gradient,x,y)
        i = i+1
                    
class App(gtk.Window):
    def __init__(self):
        gtk.Window.__init__(self)
        self.connect("destroy", gtk.main_quit)
        self.connect('key-press-event',self.key_handler)
        self.set_default_size(800,480)
        
        da = gtk.DrawingArea()
        
        da.connect('expose_event',self.expose)
    
        da.set_events(gtk.gdk.EXPOSURE_MASK
                       | gtk.gdk.LEAVE_NOTIFY_MASK
                       | gtk.gdk.BUTTON_PRESS_MASK
                       | gtk.gdk.BUTTON_RELEASE_MASK
                       | gtk.gdk.POINTER_MOTION_MASK
                       | gtk.gdk.POINTER_MOTION_HINT_MASK)
    
        self.add(da)
        self.show_all()
        
    def fill_background(self):
        w,h = self.pixmap.get_size()
        self.ctx = self.pixmap.cairo_create()
        self.ctx.set_source_rgb(0.5,0.5,0.5)
        self.ctx.rectangle(0,0,w,h)
        self.ctx.fill()
        
    def draw_objects(self):
        load_images(self.pixmap)
        
    def expose(self,widget,event):
        _,_,w,h = widget.allocation
        self.pixmap = gtk.gdk.Pixmap(widget.window,w,h)
        
        self.fill_background()
        self.draw_objects()
        
        gc = gtk.gdk.GC(widget.window)
        widget.window.draw_drawable(gc, self.pixmap, 0,0, 0,0, -1,-1)
        
    def key_handler(self,window,event):
        keyval = event.keyval
        state = event.state & gtk.accelerator_get_default_mod_mask()
        
        if keyval == keysyms.A:
            print keysyms.A

    def run(self):
        gtk.main()


if __name__ == '__main__':
    App().run()