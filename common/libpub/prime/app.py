
import os 
import cairo
from libpub.prime.widgets.image import Image
from libpub.prime.widgets.pad import Pad 
import libpub.prime.mask as mask
from libpub.prime.utils import get_image_locations,get_uniform_fit, \
    LAYOUT_STEP, LAYOUT_UNIFORM_OVERLAP,LAYOUT_UNIFORM_SPREAD

FOLDER_PATH='/photos/altimages/jyro'
#FOLDER_PATH='/mnt/bluebox/photos'

class App:
    widgetQ = []
    
    surface = None
    ctx = None
    hasChanged = True
    change_listener = None
    
    app_width = 800
    app_height = 480
    
    # Publishr app specific private members
    images = []
    
    def __init__(self):                    
        
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.app_width,self.app_height)
        self.ctx = cairo.Context(self.surface)
        
        LIMIT = 50
        # Get list of images to display
        if os.path.isdir(FOLDER_PATH):
            files = os.listdir(FOLDER_PATH)
            for f in files:
                if len(self.images) >= LIMIT:
                    break
                
                if f.lower().endswith('jpg') or  \
                    f.lower().endswith('jpeg') or  \
                    f.lower().endswith('xcf') or  \
                    f.lower().endswith('gif'):
                        self.images.append(FOLDER_PATH+os.sep+f)

        self.__load_images()
        self.__update_surface()
        
    def __load_images(self):
        imgw,imgh = get_uniform_fit(len(self.images),max_x=800,max_y=480)
        i = 0
        for (x,y) in get_image_locations(
                len(self.images),layout=LAYOUT_UNIFORM_OVERLAP,owidth=imgw,oheight=imgh):
            img = Image(self.images[i],imgw,imgh, 
                        X_MARGIN=int(0.1*imgw),Y_MARGIN=int(0.1*imgh))
            img.register_click_listener(self.on_image_click)
            self.widgetQ.append((img,x,y))
            i = i+1

    def __update_surface(self):
        # Create Image widgets for images and lay them out on the surface
        #gradient = mask.MoonRise(imgw,imgh).surface
        for widget in self.widgetQ:
            self.ctx.set_source_surface(widget[0].surface,widget[1],widget[2])
            #self.ctx.mask_surface(gradient,x,y)
            self.ctx.paint()
            
        self.hasChanged = True
        if self.change_listener:
            self.change_listener(self)
            
    def get_surface(self):
        # TODO: Is this the right place to change hasChanged?
        self.hasChanged = False
        return self.surface

    def register_change_listener(self,change_listener):
        self.change_listener = change_listener
        
    def dispatch_key_event(self,keyval,state):
        for widget in self.widgetQ:
            if hasattr(widget[0],'key_listener'):
                widget[0].key_listener(keyval,state)
                
    def dispatch_pointer_event(self,x,y,pressed):
        for widget in self.widgetQ:
            if hasattr(widget[0],'pointer_listener'):
                widget[0].pointer_listener(x-widget[1],y-widget[2],pressed)
                
    def on_image_click(self,image):
        pad = Pad(int(2*self.app_width/3),int(2*self.app_height/3))
        self.widgetQ.append((pad,int(self.app_width/3)-20,int(self.app_height/3)-20))
        self.__update_surface()