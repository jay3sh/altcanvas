import cairo
import gtk
from libpub.prime.widget import Widget

class Image(Widget):
    surface = None
    path = None
    click_listener = None
    
    def __init__(self,path,w,h,X_MARGIN=0,Y_MARGIN=0):
        Widget.__init__(self, w, h)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,w,h)
        ctx.fill()
        
        self.path = path
        ctx2 = gtk.gdk.CairoContext(ctx)
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        scaled_pixbuf = pixbuf.scale_simple(
                            w-2*X_MARGIN,h-2*Y_MARGIN,gtk.gdk.INTERP_NEAREST)
        ctx2.set_source_pixbuf(scaled_pixbuf,X_MARGIN,Y_MARGIN)
        ctx2.paint()
        
    def register_click_listener(self,click_listener):
        self.click_listener = click_listener
        
    def pointer_listener(self,x,y,pressed=False):
        oldFocus = self.hasFocus
        if x > 0 and x < self.w and y > 0 and y < 2*self.h/3:
            self.hasFocus = True
        else:
            self.hasFocus = False
            
        if not oldFocus and self.hasFocus:
            if self.click_listener:
                self.click_listener(self)
