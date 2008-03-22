
import cairo

class Entry:
    surface = None
    text = ''
    
    def get_font_extents(self,fontface,fontsize):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def __init__(self,size=10,fontface='sans-serif',fontsize=20):
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        w = int(maxx*size)
        h = int(hgt+des)
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)

        ctx.rectangle(0,0,w,h)
        ctx.set_source_rgba(0,0,0,1)
        ctx.stroke()

    def key_listener(self,key,state):
        self.text += chr(key)
        print self.text