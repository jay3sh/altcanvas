
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
import gtk
from libpub.prime.widget import Widget
from libpub.prime import utils
import libpub.prime.mask as mask

class Image(Widget):
    surface = None
    path = None
    click_listener = None
    
    __pointer_listener_enabled = True
    
    def __init__(self,path,w,h,X_MARGIN=0,Y_MARGIN=0):
        Widget.__init__(self, w, h)
        self.X_MARGIN = X_MARGIN
        self.Y_MARGIN = Y_MARGIN
        self.path = path
        
        self.draw_image()
        
    def draw_image(self):
        w = self.w
        h = self.h
        surface1 = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx1 = cairo.Context(surface1)
        
        ctx2 = gtk.gdk.CairoContext(ctx1)
        
        pixbuf = gtk.gdk.pixbuf_new_from_file(self.path)
        scaled_pixbuf = pixbuf.scale_simple(
                            w-2*self.X_MARGIN,
                            h-2*self.Y_MARGIN,gtk.gdk.INTERP_NEAREST)
        ctx2.set_source_rgb(1,1,1)
        ctx2.rectangle(0,0,w,h)
        ctx2.fill()
        ctx2.set_source_pixbuf(scaled_pixbuf,self.X_MARGIN,self.Y_MARGIN)
        ctx2.paint()
        
        # Draw this on a third surface with a gradient
        gradient = mask.MoonRise(w,h).surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx3 = cairo.Context(self.surface)
        ctx3.set_source_rgb(0,0,0)
        ctx3.rectangle(0,0,w,h)
        ctx3.fill()
        ctx3.set_source_surface(surface1)
        ctx3.mask_surface(gradient)
        
        
if utils.detect_platform() == 'Nokia':
    NOTE_PATH = '/usr/share/altpublishr/icons/note.png'
    GLOBE_PATH = '/usr/share/altpublishr/icons/globe.png'
else:
    NOTE_PATH = '/home/jayesh/workspace/altcanvas/install/note.svg'
    GLOBE_PATH = '/home/jayesh/workspace/altcanvas/install/globe.svg'

note_pixbuf = gtk.gdk.pixbuf_new_from_file(NOTE_PATH)
globe_pixbuf = gtk.gdk.pixbuf_new_from_file(GLOBE_PATH)
        
class PublishrImage(Image):
    title = None
    desc = None
    tags = None
    
    # after upload members
    url = None
    def __init__(self,path,w,h,X_MARGIN=0,Y_MARGIN=0):
        Image.__init__(self, path, w, h, X_MARGIN, Y_MARGIN)
        
    def set_info(self,title,desc,tags=None):
        self.title = title
        self.desc = desc
        self.tags = tags
        
        self.update_icon()
        
        
    def update_icon(self):
        self.draw_image()
        icon = None
        if self.title:
            icon = note_pixbuf
        
        if self.url:
            icon = globe_pixbuf
             
        if icon:
            ctx = cairo.Context(self.surface)
            ctx1 = gtk.gdk.CairoContext(ctx)
            ctx1.set_source_pixbuf(icon,
                        self.w-icon.get_width()-20,20)
            ctx1.paint()
            
        
    