
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
        
        Widget.__init__(self,w,h)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        
        # Draw shape
        ctx.set_source_rgba(ocolor.r,ocolor.g,ocolor.b,ocolor.a)
        vr = int(min(w,h)/5)
        utils.draw_rounded_rect(ctx, 0, 0, w, h, vr=vr)
        
        # Draw text
        self.text = text
        ctx.select_font_face(fontface,fontangle,fontweight)
        ctx.set_font_size(fontsize)
        x_bearing,y_bearing,width,height,x_adv,y_adv = \
            ctx.text_extents(self.text)
        
        ctx.set_source_rgba(tcolor.r,tcolor.g,tcolor.b,tcolor.a)
        ctx.move_to(int((w-width)/2),int((h-height)/2)-y_bearing)
        ctx.show_text(self.text)
        
        
    