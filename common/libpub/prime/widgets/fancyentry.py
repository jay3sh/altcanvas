
# This file is part of AltCanvas.
#
# http://code.google.com/p/altcanvas
#
# AltCanvas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AltCanvas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AltCanvas.  If not, see <http://www.gnu.org/licenses/>.




import cairo
from libpub.prime.widget import Widget


class FancyEntry(Widget):
    surface = None
    text = ''
    ctx = None
    text_ctx = None
    text_surface = None
    maxx = 0
    size = 0
    inner_margin_ratio = 1.2
    outer_margin_ratio = 1.4
    
    change_listener = None
    
    def get_font_extents(self,fontface,fontsize):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(2)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        return ctx.font_extents()
    
    def __init__(self,w=0,h=0,size=10,
                 fontface='sans-serif',fontsize=20):
        
        Widget.__init__(self,w,h)
        
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(fontface,fontsize)
        
        self.maxx = maxx
        self.size = size
        
        self.w = int(self.inner_margin_ratio*maxx*size)
        self.h = int(self.inner_margin_ratio*(hgt+des))
        
        self.wo = self.w + int(((self.outer_margin_ratio-1.0))*self.maxx)
        self.ho = int(self.outer_margin_ratio*self.h)
        self.xo = 0
        self.yo = 0
        
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.wo,self.ho)
        self.ctx = cairo.Context(self.surface)

        self.text_surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        self.text_ctx = cairo.Context(self.text_surface)
        self.text_ctx.set_line_width(2)
        self.text_ctx.set_tolerance(.1)
        self.text_ctx.select_font_face(fontface)
        self.text_ctx.set_font_size(fontsize)
        
        
        self.get_surface()
        
    def register_change_listener(self,listener):
        self.change_listener = listener
        
    def get_surface(self):
        
        # Outer rectangle - fill and border
        self.ctx.rectangle(0,0,self.wo,self.ho)
        self.ctx.set_source_rgba(1,1,1,1)
        self.ctx.fill()
        
        #self.ctx.rectangle(0,0,self.wo,self.ho)
        #self.ctx.set_source_rgba(0,0,0,1)
        #self.ctx.stroke()
        
        # Inner rectangle - fill and border
        self.text_ctx.rectangle(0,0,self.w,self.h)
        self.text_ctx.set_source_rgba(1,1,1,1)
        self.text_ctx.fill()
        
        self.text_ctx.rectangle(0,0,self.w,self.h)
        self.text_ctx.set_source_rgba(0,0,0,1)
        self.text_ctx.stroke()
        
        # Draw the text on its surface
        (x, y, width, height, dx, dy) = self.text_ctx.text_extents(self.text)
        xoff = int(((self.inner_margin_ratio-1.0)/2)*self.maxx)
        yoff = int(0.3*self.h) 
        self.text_ctx.save()
        self.text_ctx.translate(xoff+x,yoff+(-y))
        self.text_ctx.set_source_rgb(0,0,0)
        self.text_ctx.show_text(self.text)        
        self.text_ctx.restore()
        
        #xborder = int(((self.outer_margin_ratio-1.0)/2)*self.maxx)
        #yborder = int(((self.outer_margin_ratio-1.0)/2)*self.h)
        xborder = int((self.wo - self.w)/2)
        yborder = int((self.ho - self.h)/2)
        self.ctx.set_source_surface(self.text_surface,xborder,yborder)
        self.ctx.paint()
        
        # Draw gradients
        # top
        lingrad = cairo.LinearGradient(xborder,yborder,xborder,0)
        lingrad.add_color_stop_rgba(1,0,0,0,0)
        lingrad.add_color_stop_rgba(0.3,0,0,0,0.2)
        lingrad.add_color_stop_rgba(0,0,0,0,1)
        self.ctx.move_to(0,0)
        self.ctx.line_to(xborder,yborder)
        self.ctx.line_to(self.wo-xborder,yborder)
        self.ctx.line_to(self.wo,0)
        self.ctx.line_to(0,0)
        self.ctx.set_source(lingrad)
        self.ctx.fill()
        
        # right
        lingrad = cairo.LinearGradient(self.wo-xborder,yborder,self.wo,yborder)
        lingrad.add_color_stop_rgba(1,0,0,0,0)
        lingrad.add_color_stop_rgba(0.3,0,0,0,0.2)
        lingrad.add_color_stop_rgba(0,0,0,0,1)
        self.ctx.move_to(self.wo,0)
        self.ctx.line_to(self.wo,self.ho)
        self.ctx.line_to(self.wo-xborder,self.ho-yborder)
        self.ctx.line_to(self.wo-xborder,yborder)
        self.ctx.line_to(self.wo,0)
        self.ctx.set_source(lingrad)
        self.ctx.fill()
        
        # bottom
        lingrad = cairo.LinearGradient(self.wo-xborder,self.ho-yborder,
                                           self.wo-xborder,self.ho)
        lingrad.add_color_stop_rgba(1,0,0,0,0)
        lingrad.add_color_stop_rgba(0.3,0,0,0,0.2)
        lingrad.add_color_stop_rgba(0,0,0,0,1)
        self.ctx.move_to(self.wo,self.ho)
        self.ctx.line_to(0,self.ho)
        self.ctx.line_to(xborder,self.ho-yborder)
        self.ctx.line_to(self.wo-xborder,self.ho-yborder)
        self.ctx.line_to(self.wo,self.ho)
        self.ctx.set_source(lingrad)
        self.ctx.fill()
        
        # left
        lingrad = cairo.LinearGradient(xborder,yborder,0,yborder)
        lingrad.add_color_stop_rgba(1,0,0,0,0)
        lingrad.add_color_stop_rgba(0.3,0,0,0,0.2)
        lingrad.add_color_stop_rgba(0,0,0,0,1)
        self.ctx.move_to(0,self.ho)
        self.ctx.line_to(0,0)
        self.ctx.line_to(xborder,yborder)
        self.ctx.line_to(xborder,self.ho-yborder)
        self.ctx.line_to(0,self.ho)
        self.ctx.set_source(lingrad)
        self.ctx.fill()
            
        return self.surface
        
    def key_listener(self,key,state):
        self.text += chr(key)
        if self.change_listener:
            self.get_surface()
            self.change_listener.on_surface_change(self)
        
    def pointer_listener(self,x,y,pressed=False):
        oldFocus = self.hasFocus
        if x > 0 and x < self.w and y > 0 and y < self.h:
            self.hasFocus = True
        else:
            self.hasFocus = False
            