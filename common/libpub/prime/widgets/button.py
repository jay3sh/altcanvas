
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
from libpub.prime import utils
from libpub.prime.utils import RGBA


class Button(Widget):
    text = ''
    
    def __init__(self,w,h,text,
                 fontface='sans-serif',
                 fontangle=cairo.FONT_SLANT_NORMAL,
                 fontweight=cairo.FONT_WEIGHT_NORMAL,
                 fontsize=20,
                 icolor=RGBA(),    # in Focus color
                 ocolor=RGBA(),    # out of Focus color
                 bcolor=RGBA(),    # border color
                 tcolor=RGBA()):   # text color
        
        self.fontface = fontface
        self.fontweight = fontweight
        self.fontsize = fontsize
        self.fontangle = fontangle
        self.icolor = icolor
        self.ocolor = ocolor
        self.bcolor = bcolor
        self.tcolor = tcolor
        self.text = text
        
        Widget.__init__(self,w,h)
        
        self.redraw()
        
        
    def redraw(self):
        ocolor = self.ocolor
        tcolor = self.tcolor
        w = self.w
        h = self.h
        # Draw shape
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        ctx.set_source_rgba(ocolor.r,ocolor.g,ocolor.b,ocolor.a)
        vr = int(min(w,h)/5)
        utils.draw_rounded_rect(ctx, 0, 0, w, h, vr=vr)
        
        # Draw text
        ctx.select_font_face(self.fontface,self.fontangle,self.fontweight)
        ctx.set_font_size(self.fontsize)
        x_bearing,y_bearing,width,height,x_adv,y_adv = \
            ctx.text_extents(self.text)
        
        ctx.set_source_rgba(tcolor.r,tcolor.g,tcolor.b,tcolor.a)
        ctx.move_to(int((w-width)/2),int((h-height)/2)-y_bearing)
        ctx.show_text(self.text)
        
        
    
class DropdownButton(Widget):
    def __init__(self,w,h):
        Widget.__init__(self,w,h)
        self.redraw()

    def redraw(self):
        from math import pi as PI
        w = self.w
        h = self.h
        r = int(min(w,h)/2)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)

        ctx.set_source_rgb(0.2,0.2,0.2)
        ctx.arc(w/2,h/2,r,0,2*PI)
        ctx.fill()

        ctx.set_source_rgb(0.8,0.8,0.8)
        pts = ((w/5,h/4),(4*w/5,h/4),(w/2,3*h/4))

        ctx.move_to(pts[2][0],pts[2][1])
        for pt in pts:
            ctx.line_to(pt[0],pt[1])
        ctx.fill()



