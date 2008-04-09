
import cairo
from libpub.prime.widget import Widget
from libpub.prime.utils import RGBA,show_multiline

class Label(Widget):
    
    def get_font_extents(self,fontface,fontsize,fontangle,fontweight):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,0,0)
        ctx = cairo.Context(surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def calculate_num_lines(self,w,text,fontface,fontsize,fontangle,fontweight):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,0,0)
        ctx = cairo.Context(surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        
        line = 0
        used = 0
        _,_,_,_,space_x_adv,_ = ctx.text_extents(str(' '))
        
        for word in text.split(' '):
            _,_,width,_,x_adv,_ = ctx.text_extents(word)
            if( used > 0 and used+width >= w):
                used = 0
                line += 1
            used += x_adv + space_x_adv
        line += 1
        return line
    
    
    def __init__(self,text,fontface='sans-serif',
                 fontangle=cairo.FONT_SLANT_NORMAL,
                 fontweight=cairo.FONT_WEIGHT_NORMAL,
                 fontsize=0,w=0,color=RGBA()):
        
        if not w or not fontsize:
            raise Exception('width OR fontsize should be supplied')
            
        x_margin = 10
        y_margin = 10
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(
                                    fontface,fontsize,fontangle,fontweight)
        
        num_lines = self.calculate_num_lines(
                                    w,text,fontface,fontsize,fontangle,fontweight)
        
        hi = int(hgt+des)
        
        h = num_lines * hi + y_margin
        
        
        Widget.__init__(self, w=w, h=h)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        
        ctx.set_source_rgba(color.r,color.g,color.b,color.a)
            
        show_multiline(w,hi,ctx,text,y_margin)
    