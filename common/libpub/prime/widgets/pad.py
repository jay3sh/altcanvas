
import cairo
from libpub.prime.widget import Widget
import libpub.prime.mask as mask

class Pad(Widget):
    surface = None
    
    def __init__(self,w,h):
        Widget.__init__(self,w,h)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgba(0.3,0.3,0.3,0.99)
        lgrad = mask.Linear(w,h).surface
        ctx.rectangle(0,0,w,h)
        ctx.mask_surface(lgrad)
        
    