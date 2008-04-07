
import cairo
from libpub.prime.widget import Widget
from libpub.prime.utils import RGBA

class Label(Widget):
    
    def get_font_extents(self,fontface,fontsize,fontangle,fontweight):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def calculate_num_lines(self,text,fontface,fontsize,fontangle,fontweight):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
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
                                    text,fontface,fontsize,fontangle,fontweight)
        
        h = num_lines * int(hgt+des) + y_margin
        
        hi = int(hgt+des)
        
        Widget.__init__(self, w=w, h=h)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        
        ctx.set_source_rgba(color.r,color.g,color.b,color.a)
        
        # @summary: word by word drawing, center justified
        used = 0 
        line = 0
        line_text = ''
        _,_,_,_,space_x_adv,_ = ctx.text_extents(str(' '))
        for word in text.split(' '):
        
            x_bearing,y_bearing,width,height,x_adv,y_adv = ctx.text_extents(word)
            
            if( used > 0 and used+width >= w):
                x_b,y_b,wdt,hgt,x_a,y_a = ctx.text_extents(line_text)
                ctx.move_to(x_b+int((w-used)/2),line*hi+y_margin-y_b)
                ctx.show_text(line_text)
                line_text = ''
                used = 0 
                line += 1
                
            line_text += word+' '
                
            used += x_adv + space_x_adv
            
            
        # Deal with remaining text
        if line_text != '':
            x_bearing,y_bearing,width,height,x_adv,y_adv = ctx.text_extents(line_text)
            ctx.move_to(x_bearing+int((w-used)/2),line*hi+y_margin-y_bearing)
            ctx.show_text(line_text)
            
    