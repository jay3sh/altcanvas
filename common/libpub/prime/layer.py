from libpub.prime.widgetq import WidgetQueue
from libpub.prime.widget import WidgetWrapper

from libpub.prime.utils import * 

from libpub.prime.widgets.pad import Pad
from libpub.prime.widgets.image import Image 


class Layer:
    
    widgetQ = None
    
    isVisible = False
    
    def __init__(self,isVisible=True):
        self.widgetQ = WidgetQueue()
        self.isVisible = isVisible
    
    
class ImageLayer(Layer):
    # App specific members
    background = None
    images = None
    
    app_width = 800
    app_height = 480
    
    def __init__(self,isVisible=True,images=None):
        Layer.__init__(self, isVisible)
        self.images = images
        
        # Background
        if not self.background:
            
            self.background = Pad(self.app_width,self.app_height, 
                                 texture=Pad.WALLPAPER,shape=Pad.RECT)
            
            # TODO
            #self.background.register_tap_listener(self.on_background_tap)
            
            log.writeln('BG (%s)'%(self.background.id_str))
            
        self.widgetQ.append(WidgetWrapper(self.background,0,0))
            
        # Images
        imgw,imgh = get_uniform_fit(len(self.images),
                                max_x=self.app_width,max_y=self.app_height)
        i = 0
        
        for (x,y) in get_image_locations(
                len(self.images),layout=LAYOUT_UNIFORM_OVERLAP,
                owidth=imgw,oheight=imgh):
            
            img = Image(self.images[i],imgw,imgh, 
                        X_MARGIN=int(0.05*imgw),Y_MARGIN=int(0.05*imgh))
            
            log.writeln('%s (%s)'%(img.path,img.id_str))
            
            # TODO
            #img.register_click_listener(self.on_image_click)
            
            self.widgetQ.append(WidgetWrapper(img,x,y))
            
            i = i+1

    def draw(self,ctx):
        for ww in self.widgetQ.next():
            ctx.set_source_surface(ww.widget.surface,ww.x,ww.y)
            ctx.paint()
