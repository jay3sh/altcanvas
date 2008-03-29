
import os 
import cairo
from libpub.prime.widgets.image import Image
import libpub.prime.mask as mask
from libpub.prime.utils import get_image_locations,LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD

FOLDER_PATH='/photos/altimages/jyro'

class App:
    widgetQ = []
    
    surface = None
    ctx = None
    
    # Publishr app specific private members
    images = []
    
    def __init__(self):                    
        '''
            @param x: X coordinate of App's upper left corner on canvas 
            @param y: Y coordinate of App's upper left corner on canvas
        '''
        
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,800,480)
        self.ctx = cairo.Context(self.surface)
        
        # Get list of images to display
        if os.path.isdir(FOLDER_PATH):
            files = os.listdir(FOLDER_PATH)
            for f in files:
                if f.lower().endswith('jpg') or  \
                    f.lower().endswith('jpeg') or  \
                    f.lower().endswith('xcf') or  \
                    f.lower().endswith('gif'):
                        self.images.append(FOLDER_PATH+os.sep+f)

        self.__update_surface()

    def __update_surface(self):
        # Create Image widgets for images and lay them out on the surface
        gradient = mask.Linear(150,150).surface
        i = 0
        for (x,y) in get_image_locations(
                len(self.images),layout=LAYOUT_UNIFORM_SPREAD):
            img = Image(self.images[i],150,150)
            self.ctx.set_source_surface(img.surface,x,y)
            self.ctx.mask_surface(gradient,x,y)
            i = i+1
            
    def get_surface(self):
        return self.surface
