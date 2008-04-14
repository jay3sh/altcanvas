import cairo
import gtk
from libpub.prime.widget import Widget
from libpub.prime import utils
import libpub.prime.mask as mask

class Image(Widget):
    surface = None
    path = None
    click_listener = None
    
    __pointer_listener_enabled = True
    
    def __init__(self,path,w,h,X_MARGIN=0,Y_MARGIN=0):
        Widget.__init__(self, w, h)
        surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx1 = cairo.Context(surface1)
        
        ctx2 = gtk.gdk.CairoContext(ctx1)
        
        self.path = path
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        scaled_pixbuf = pixbuf.scale_simple(
                            w-2*X_MARGIN,h-2*Y_MARGIN,gtk.gdk.INTERP_NEAREST)
        ctx2.set_source_rgb(1,1,1)
        ctx2.rectangle(0,0,w,h)
        ctx2.fill()
        ctx2.set_source_pixbuf(scaled_pixbuf,X_MARGIN,Y_MARGIN)
        ctx2.paint()
        
        # Draw this on a third surface with a gradient
        gradient = mask.MoonRise(w,h).surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx3 = cairo.Context(self.surface)
        ctx3.set_source_rgb(0,0,0)
        ctx3.rectangle(0,0,w,h)
        ctx3.fill()
        ctx3.set_source_surface(surface1)
        ctx3.mask_surface(gradient)
        
        
if utils.detect_platform() == 'Nokia':
    TICK_PATH = '/mnt/bluebox/altcanvas/install/tick.png'
else:
    TICK_PATH = '/home/jayesh/workspace/altcanvas/install/tick.svg'
        
class PublishrImage(Image):
    title = None
    desc = None
    tags = None
    def __init__(self,path,w,h,X_MARGIN=0,Y_MARGIN=0):
        Image.__init__(self, path, w, h, X_MARGIN, Y_MARGIN)
        
    def set_info(self,title,desc,tags=None):
        self.title = title
        self.desc = desc
        self.tags = tags
        
        if self.title:
            ctx = cairo.Context(self.surface)
            ctx1 = gtk.gdk.CairoContext(ctx)
            pixbuf = gtk.gdk.pixbuf_new_from_file(TICK_PATH)
            ctx1.set_source_pixbuf(pixbuf,0,0)
            ctx1.paint()
            
        
    