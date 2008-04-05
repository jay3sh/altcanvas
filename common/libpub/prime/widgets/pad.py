
import gtk
import cairo
from libpub.prime.widget import Widget
import libpub.prime.mask as mask
from libpub.prime import utils

from libpub.prime.utils import RGBA

class Pad(Widget):
    (PLAIN,RECT_GRAD_EXPLOSION,WALLPAPER) = range(3)
    surface = None
    
    def __init__(self,w,h,color=RGBA(0,0,0,1),type=PLAIN):
        Widget.__init__(self,w,h)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        
        if type == self.RECT_GRAD_EXPLOSION:
            BORDER = int(min(w,h)*0.25) 
            border_surface = utils.draw_grad_rect(
                                inner=(BORDER/2,BORDER/2,w-BORDER,h-BORDER),
                                border=BORDER,color=color)
        
            ctx.set_source_surface(border_surface)
            ctx.paint()
            
            ctx.set_source_rgba(color.r,color.b,color.b,color.a)
            ctx.rectangle(BORDER/2,BORDER/2,w-BORDER,h-BORDER)
            ctx.fill()
        
        elif type == self.PLAIN:
            ctx.set_source_rgba(color.r,color.b,color.b,color.a)
            ctx.rectangle(0,0,w,h)
            ctx.fill()
            
        elif type == self.WALLPAPER:
            ctx1 = gtk.gdk.CairoContext(ctx)
            pixbuf = gtk.gdk.pixbuf_new_from_file(
                        '/home/jayesh/workspace/altcanvas/install/altpublishr.svg')
            ctx1.set_source_pixbuf(pixbuf,0,0)
            ctx1.paint()
            
    