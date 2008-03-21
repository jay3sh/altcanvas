import cairo
import gtk

class Image:
    surface = None
    
    def __init__(self,path,w,h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx2 = gtk.gdk.CairoContext(ctx)
        pixbuf = gtk.gdk.pixbuf_new_from_file(path)
        scaled_pixbuf = pixbuf.scale_simple(w,h,gtk.gdk.INTERP_NEAREST)
        ctx2.set_source_pixbuf(scaled_pixbuf,0,0)
        ctx2.paint()