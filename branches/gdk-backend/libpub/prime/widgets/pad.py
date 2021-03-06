
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



import gtk
import cairo
from math import pi as PI
import libpub
from libpub.prime.widget import Widget
import libpub.prime.mask as mask
from libpub.prime import utils
from libpub.prime.utils import RGBA

WALLPAPER_PATH = libpub.IMAGE_DIR+'/altpublishr.png'

class Pad(Widget):
    (RECT,ROUNDED_RECT) = range(2)
    (PLAIN,GRAD_EXPLOSION,WALLPAPER) = range(3)
    
    def __init__(self,w,h,color=RGBA(0,0,0,1),texture=PLAIN,shape=RECT):
        Widget.__init__(self,w,h)
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(self.surface)
        
        if texture == self.GRAD_EXPLOSION:
            BORDER = int(min(w,h)*0.25) 
            border_surface = utils.draw_grad_rect(
                                inner=(BORDER/2,BORDER/2,w-BORDER,h-BORDER),
                                border=BORDER,color=color)
        
            ctx.set_source_surface(border_surface)
            ctx.paint()
            
            ctx.set_source_rgba(color.r,color.g,color.b,color.a)
            ctx.rectangle(BORDER/2,BORDER/2,w-BORDER,h-BORDER)
            ctx.fill()
        
        elif texture == self.PLAIN and shape == self.RECT:
            ctx.set_source_rgba(color.r,color.g,color.b,color.a)
            ctx.rectangle(0,0,w,h)
            ctx.fill()
            
        elif texture == self.PLAIN and shape == self.ROUNDED_RECT:
            ctx.set_source_rgba(color.r,color.g,color.b,color.a)
            utils.draw_rounded_rect(ctx, 0, 0, w, h)
            '''
            x0 = 0
            y0 = 0
            x1 = x0+w
            y1 = y0+h
            vr = int(min(w,h)/10)
            
            ctx.set_source_rgba(color.r,color.g,color.b,color.a)
            
            ctx.move_to(x0+vr,y0)
            ctx.line_to(x1-vr,y0)
            ctx.arc(x1-vr,y0+vr,vr,3*PI/2,0)
            ctx.line_to(x1,y1-vr)
            ctx.arc(x1-vr,y1-vr,vr,0,PI/2)
            ctx.line_to(x0+vr,y1)
            ctx.arc(x0+vr,y1-vr,vr,PI/2,PI)
            ctx.line_to(x0,y0+vr)
            ctx.arc(x0+vr,y0+vr,vr,PI,3*PI/2)
            
            ctx.fill()
            '''
            
        elif texture == self.WALLPAPER:
            ctx1 = gtk.gdk.CairoContext(ctx)
            pixbuf = gtk.gdk.pixbuf_new_from_file(WALLPAPER_PATH)
            ctx1.set_source_pixbuf(pixbuf,0,0)
            ctx1.paint()
            
