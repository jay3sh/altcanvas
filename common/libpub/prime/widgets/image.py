
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

        print (w,h,self.X_MARGIN,self.Y_MARGIN)
        png_path = None
        if not self.path.lower().endswith('png'):
            from PIL import Image
            png_path = self.path+'.png'
            im = Image.open(self.path)
            im.thumbnail((w-2*self.X_MARGIN,h-2*self.Y_MARGIN),
                            Image.ANTIALIAS)
            im.save(png_path)
            imgSurface = cairo.ImageSurface.create_from_png(png_path)
        else:
            imgSurface = cairo.ImageSurface.create_from_png(self.path)

        imgCtx = cairo.Context(imgSurface)
        #sx = (w-2*self.X_MARGIN)*1.0/imgSurface.get_width()
        #sy = (w-2*self.Y_MARGIN)*1.0/imgSurface.get_height()

        #gradient = mask.MoonRise(w,h).surface
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx3 = cairo.Context(self.surface)
        ctx3.set_source_rgba(1,1,1,0.7)
        ctx3.rectangle(0,0,w,h)
        ctx3.fill()
        #ctx3.scale(sx,sy)
        ctx3.set_source_surface(imgSurface,self.X_MARGIN,self.Y_MARGIN)
        #ctx3.mask_surface(gradient)
        ctx3.paint()
        
        if png_path:
            import os
            os.remove(png_path)
        
import libpub
NOTE_PATH = libpub.IMAGE_DIR+'/note.png'
GLOBE_PATH = libpub.IMAGE_DIR+'/globe.png'

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
        # Image info is edited, mark with a Note icon
        if self.title:
            icon = NOTE_PATH
        
        # Image if uploaded, mark with a Web URL icon
        if self.url:
            icon = GLOBE_PATH
             
        if icon:
            iconSurface = cairo.ImageSurface.create_from_png(icon)
            ctx = cairo.Context(self.surface)
            ctx.set_source_surface(iconSurface,
                        self.w-iconSurface.get_width()-20,20)
            ctx.paint()
            
        
    
