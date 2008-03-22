
import cairo
import gtk

class Linear:
    surface = None
    
    def __init__(self,w,h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        lingrad = cairo.LinearGradient(0.0,0.0,w,h)
        lingrad.add_color_stop_rgba(1,0,0,0,1)
        lingrad.add_color_stop_rgba(0.25,0,0,0,0.75)
        lingrad.add_color_stop_rgba(0,0,0,0,0)
        rect = ctx.rectangle(0,0,w,h)
        ctx.set_source(lingrad)
        ctx.fill()
    
    