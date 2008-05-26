
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
from libpub.prime.utils import RGBA,show_multiline

class Label(Widget):
    text = None
    
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
        
        self.text = text
        self.fontface = fontface
        self.fontangle = fontangle
        self.fontweight = fontweight
        self.fontsize = fontsize
        self.color = color
        
        if not w or not fontsize:
            raise Exception('width OR fontsize should be supplied')
            
        self.x_margin = 10
        self.y_margin = 10
        
        asc,des,hgt,maxx,maxy = self.get_font_extents(
                                    fontface,fontsize,fontangle,fontweight)
        
        num_lines = self.calculate_num_lines(
                                    w,self.text,fontface,fontsize,fontangle,fontweight)
        
        self.hi = int(hgt+des)
        
        h = num_lines * self.hi + self.y_margin
        
        Widget.__init__(self, w=w, h=h)
        
        self.redraw()
        
    def redraw(self):
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)
        ctx = cairo.Context(self.surface)
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(self.fontface,self.fontangle,self.fontweight)
        ctx.set_font_size(self.fontsize)
        
        ctx.set_source_rgba(self.color.r,self.color.g,self.color.b,self.color.a)
            
        show_multiline(self.w,self.hi,ctx,self.text,self.y_margin)
    