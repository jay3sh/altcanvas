
import cairo
from libpub.prime.widget import Widget

class Entry(Widget):
    surface = None
    text = ''
    parent = None
    ctx = None
    
    def get_font_extents(self,fontface,fontsize):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def __init__(self,parent=0,x=0,y=0,w=0,h=0,size=10,fontface='sans-serif',fontsize=20):
        
        Widget.__init__(self,x,y,w,h)
        self.parent = parent
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        self.w = int(maxx*size)
        self.h = int(hgt+des)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_line_width(6)
        self.ctx.set_tolerance(.1)
        self.ctx.select_font_face(fontface)

    def get_surface(self):
        w = self.w
        h = self.h
        
        self.ctx.rectangle(0,0,w,h)
        self.ctx.set_source_rgba(1,1,1,1)
        self.ctx.fill()
        
        self.ctx.rectangle(0,0,w,h)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.stroke()
        
        (x, y, width, height, dx, dy) = self.ctx.text_extents(self.text)
        x_margin = 10
        y_margin = 10
        self.ctx.save()
        self.ctx.translate(x_margin+x,y_margin+(-y))
        self.ctx.set_source_rgb(0,0,0)
        self.ctx.show_text(self.text)        
        self.ctx.restore()
        
        return self.surface
    
        
    def key_listener(self,key,state):
        self.text += chr(key)
        self.parent.queue_draw()
        print self.text