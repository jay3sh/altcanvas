
import cairo
from libpub.prime.widget import Widget

class Label(Widget):
    
    def get_font_extents(self,fontface,fontsize):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def __init__(self,text,fontface='sans-serif',fontsize=20):
        Widget.__init__(self, w=0, h=0)
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        self.w = int(maxx*len(text))
        self.h = int(hgt+des)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        (x, y, width, height, dx, dy) = ctx.text_extents(text)
        
    
        x_margin = 10
        y_margin = 10
        ctx.translate(x_margin+x,y_margin+(-y))
        ctx.set_source_rgb(1,1,1)
        ctx.show_text(text)