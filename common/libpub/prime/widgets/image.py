import cairo
import gtk
from libpub.prime.widget import Widget
import libpub.prime.mask as mask

class Image(Widget):
    surface = None
    path = None
    click_listener = None
    
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
        
    def register_click_listener(self,click_listener):
        self.click_listener = click_listener
        
    def pointer_listener(self,x,y,pressed=False):
        oldFocus = self.hasFocus
        
        if x > 0 and x < self.w and y > 0 and y < self.h:
            # Check if we are under any cloud
            for cloud in self.clouds:
            	if x > cloud[0] and x < cloud[2] and y > cloud[1] and y < cloud[3]:
                    self.hasFocus = False
            	    return
            # We are not under any cloud
            self.hasFocus = True
        else:
            self.hasFocus = False
            
        if not oldFocus and self.hasFocus:
            if self.click_listener:
                self.click_listener(self)
