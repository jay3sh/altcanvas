
import cairo
import gtk
from math import pi as PI

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
        
class LinearExplosion:
    surface = None
    
    def __init__(self,w,h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        
        grad = cairo.LinearGradient(int(w/2),int(2*h/3),int(w/2),h)
        grad.add_color_stop_rgba(1,0,0,0,0)
        grad.add_color_stop_rgba(0.66,0,0,0,0.33)
        grad.add_color_stop_rgba(0,0,0,0,1)
        rect = ctx.rectangle(0,0,w,h)
        ctx.set_source(grad)
        ctx.fill()
        
        '''
        cx = w/2
        cy = h/2
        # Don't know how this works
        g1 = cairo.LinearGradient(cx,cy,w/2,0)
        g2 = cairo.LinearGradient(cx,cy,w,h/2)
        g3 = cairo.LinearGradient(cx,cy,w/2,h)
        g4 = cairo.LinearGradient(cx,cy,0,h/2)
        
        rect = ctx.rectangle(0,0,w,h)
        
        for g in (g1,g2,g3,g4):
            g.add_color_stop_rgba(1,0,0,0,1)
            #g.add_color_stop_rgba(0.66,0,0,0,0.33)
            g.add_color_stop_rgba(0,0,0,0,0)
            
            ctx.set_source(g)
            ctx.fill()
        '''
            
    
class Radial:
    surface = None
    
    def __init__(self,w,h):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        if w > h:
            r = (w/2)
        else:
            r = (h/2)
        x0,y0 = (w/2,h/2)
        x1,y1 = (r,r)
        radgrad = cairo.RadialGradient(x0,y0,0,x0,y0,r)
        radgrad.add_color_stop_rgba(1,0,0,0,0)
        radgrad.add_color_stop_rgba(0,0,0,0,1)
        arc = ctx.arc(x0,y0,r,0,2*PI)
        ctx.set_source(radgrad)
        ctx.fill()
    