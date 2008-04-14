
import cairo
from libpub.prime.widget import Widget
from libpub.prime.utils import RGBA,show_multiline
import libpub

class Entry(Widget):
    text = ''
    top_clearing = 0
    line_width = 2
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
                 num_lines=1,
                 label='',
                 fontface='sans-serif',
                 fontangle=cairo.FONT_SLANT_NORMAL,
                 fontweight=cairo.FONT_WEIGHT_NORMAL,
                 fontsize=20,
                 icolor=RGBA(),    # in Focus color
                 ocolor=RGBA(),    # out of Focus color
                 bcolor=RGBA(),    # border color
                 tcolor=RGBA()):   # text color
        
        Widget.__init__(self,w=w,h=0)
        
        self.num_lines = num_lines
        self.fontsize = fontsize
        self.icolor = icolor
        self.ocolor = ocolor
        self.bcolor = bcolor
        self.tcolor = tcolor
        self.label = label
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        # Leave some room for label text
        self.top_clearing = int((hgt+des)/2)
        
        self.h = int(1.4*num_lines*(hgt+des)+self.top_clearing)
        
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        self.ctx = cairo.Context(self.surface)
        self.ctx.set_line_width(4)
        self.ctx.set_tolerance(.1)
        self.ctx.select_font_face(fontface,fontangle,fontweight)
        self.ctx.set_font_size(fontsize)
        
        self.redraw()
        
    def redraw_label(self):
        if not self.label:
            return
        
        x_label_margin = 5
        
        self.ctx.save()
        
        self.ctx.set_font_size(int(2*self.fontsize/3))
        x_bearing,y_bearing,width,height,x_adv,y_adv = \
            self.ctx.text_extents(self.label)
        
        # Draw label background rectangle
        self.ctx.set_source_rgba(self.ocolor.r,self.ocolor.g,
                                 self.ocolor.b,self.ocolor.a)
        self.ctx.rectangle(self.w-width-x_label_margin,0,
                           width,self.top_clearing-self.line_width)
        self.ctx.fill()
        
        
        # Draw the label text
        self.ctx.set_source_rgba(self.tcolor.r,self.tcolor.g,
                                 self.tcolor.b,self.tcolor.a)
            
        self.ctx.move_to(self.w-width-x_label_margin,-y_bearing)
        self.ctx.show_text(self.label)
        
        self.ctx.restore()
        

    def redraw(self):
        w = self.w
        h = self.h
        
        ##
        # Draw background
        self.ctx.rectangle(0,self.top_clearing,w,h-self.top_clearing)
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
        self.ctx.rectangle(0,self.top_clearing,w,h-self.top_clearing)
        self.ctx.set_line_width(self.line_width)
        self.ctx.set_source_rgba(self.bcolor.r,self.bcolor.g,
                                 self.bcolor.b,self.bcolor.a)
        self.ctx.stroke()
        self.ctx.restore()
        
        ##
        # draw text
        
        (x, y, width, height, dx, dy) = self.ctx.text_extents(self.text)
        x_margin = 10
        y_margin = self.top_clearing + 10
        
        hi = height
        self.ctx.set_source_rgba(self.tcolor.r,self.tcolor.g,
                                 self.tcolor.b,self.tcolor.a)
        show_multiline(w,hi,self.ctx,self.text,y_margin)
        
        self.redraw_label()
        
    KEY_BACKSPACE = 65288
    KEY_ENTER = 65293
    def key_listener(self,key,state):
        if self.hasFocus:
            if key == self.KEY_BACKSPACE:
                self.text = self.text[:len(self.text)-1]
            elif int(key) > 256:
                # ignore 
                # We are not supporting non-character keys
                pass
            else:
                self.text += chr(key)
                    
            self.redraw()
            libpub.prime.canvas.redraw()
        
    def pointer_listener(self,x,y,pressed=False):
        Widget.pointer_listener(self, x, y, pressed)
        if self.gainedFocus or self.lostFocus:
            self.redraw()
            libpub.prime.canvas.redraw()
        
            
            