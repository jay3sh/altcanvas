
import cairo
from libpub.prime.widget import Widget
from libpub.prime.utils import RGBA

class Entry(Widget):
    text = ''
    parent = None
    ctx = None
    
    def get_font_extents(self,fontface,fontsize):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def __init__(self,w=0,
                 fontface='sans-serif',
                 fontangle=cairo.FONT_SLANT_NORMAL,
                 fontweight=cairo.FONT_WEIGHT_NORMAL,
                 fontsize=20,
                 icolor=RGBA(),    # in Focus color
                 ocolor=RGBA(),    # out of Focus color
                 bcolor=RGBA(),    # border color
                 tcolor=RGBA()):   # text color
        
        Widget.__init__(self,w=w,h=0)
        
        self.icolor = icolor
        self.ocolor = ocolor
        self.bcolor = bcolor
        self.tcolor = tcolor
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        #self.w = int(maxx*size)
        self.h = int(1.2*(hgt+des))
        
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_line_width(4)
        self.ctx.set_tolerance(.1)
        self.ctx.select_font_face(fontface,fontangle,fontweight)
        self.ctx.set_font_size(fontsize)
        
        self.__draw()

    def __draw(self):
        w = self.w
        h = self.h
        
        ##
        # Draw background
        self.ctx.rectangle(0,0,w,h)
        if self.hasFocus:
            self.ctx.set_source_rgba(self.icolor.r,self.icolor.g,
                                     self.icolor.b,self.icolor.a)
        else:
            self.ctx.set_source_rgba(self.ocolor.r,self.ocolor.g,
                                     self.ocolor.b,self.ocolor.a)
        self.ctx.fill()
        
        ##
        # Draw border 
        self.ctx.save()
        self.ctx.rectangle(0,0,w,h)
        self.ctx.set_line_width(2)
        self.ctx.set_source_rgba(self.bcolor.r,self.bcolor.g,
                                 self.bcolor.b,self.bcolor.a)
        self.ctx.stroke()
        self.ctx.restore()
        
        (x, y, width, height, dx, dy) = self.ctx.text_extents(self.text)
        x_margin = 10
        y_margin = 10
        self.ctx.save()
        self.ctx.move_to(x_margin+x,y_margin+(-y))
        self.ctx.set_source_rgba(self.tcolor.r,self.tcolor.g,
                                 self.tcolor.b,self.tcolor.a)
        self.ctx.show_text(self.text)        
        self.ctx.restore()
        
    def register_change_listener(self,listener):
        self.change_listener = listener
        
    def key_listener(self,key,state):
        if self.hasFocus:
            self.text += chr(key)
            self.__draw()
            if self.change_listener:
                self.change_listener.on_surface_change(self)
        
    def pointer_listener(self,x,y,pressed=False):
        Widget.pointer_listener(self, x, y, pressed)
        
            
            