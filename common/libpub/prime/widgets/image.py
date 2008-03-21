import cairo
import gtk

class Image:
    surface = None
    
    def __init__(self,path,w,h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgb(1,1,1)
        ctx.rectangle(0,0,w,h)
        ctx.fill()
        
        ctx2 = gtk.gdk.CairoContext(ctx)
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        scaled_pixbuf = pixbuf.scale_simple(w-20,h-20,gtk.gdk.INTERP_NEAREST)
        ctx2.set_source_pixbuf(scaled_pixbuf,10,10)
        ctx2.paint()