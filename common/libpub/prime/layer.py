from libpub.prime.widgetq import WidgetQueue
from libpub.prime.widget import WidgetWrapper

from libpub.prime.utils import * 

from libpub.prime.widgets.pad import Pad
from libpub.prime.widgets.image import Image 

from libpub.prime.logic import on_image_click

class Layer:
    
    widgetQ = None
    
    isVisible = False
    
    # Yes this will be a generic property
    app_width = 800
    app_height = 480
    
    
    def __init__(self,isVisible=True):
        self.widgetQ = WidgetQueue()
        self.isVisible = isVisible
    
    def draw(self,ctx):
        for ww in self.widgetQ.next():
            ctx.set_source_surface(ww.widget.surface,ww.x,ww.y)
            ctx.paint()
    
class ImageLayer(Layer):
    # App specific members
    background = None
    images = None
    
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
            img.register_click_listener(on_image_click)
            
            self.widgetQ.append(WidgetWrapper(img,x,y))
            
            i = i+1


class InputLayer(Layer):
    background = None
    imageOnPad = None
    imageLabel = None
    
    def __init__(self):
        padcolor = RGBA()
        padcolor.r,padcolor.g,padcolor.b = html2rgb(0x0F,0x0F,0x0F)
        padcolor.a = 0.85
        self.background = Pad(int(5*self.app_width/6),int(5*self.app_height/6),
                            color=padcolor,texture=Pad.PLAIN,
                            shape=Pad.ROUNDED_RECT)
    
        self.px = int(self.app_width/12)
        self.py = int(self.app_height/12)
        
        if not self.widgetQ.hasWidget(self.background):
            self.widgetQ.append(WidgetWrapper(self.background,self.px,self.py))

        if detect_platform() == 'Nokia':
            self.NUM_STEPS = 3
        else:
            self.NUM_STEPS = 13 

    def show_image(self,image):
        # Detect if incoming image is the same one on the pad
        if self.imageOnPad and image.id == self.imageOnPad.widget.id:
            return

        ipx = self.px + int(self.app_width/20)
        ipy = self.py + int(self.app_height/3 - image.h/2)
        
        # Put the name of image on a label below the image
        path = self.imageOnPad.widget.path
        imgName = path[path.rfind('/')+1:path.rfind('.')]
        if self.labelOnPad:
            self.widgetQ.remove(self.labelOnPad)
            
        self.labelOnPad = Label(imgName,w=self.imageOnPad.widget.h,
                                fontface='Sans Serif',
                                fontweight=cairo.FONT_WEIGHT_BOLD,
                                fontsize=20,
                                color=RGBA(1,1,1,1))
            
        self.widgetQ.append(WidgetWrapper(self.labelOnPad,ipx,ipy+image.h+10))
        
        lpx = self.px + int(self.app_width/20) + image.w + \
                        int(self.app_width/20)
        lpy = self.py + 5*self.app_height/12
        
        icolor = RGBA()
        icolor.r,icolor.g,icolor.b = html2rgb(0x3F,0x3F,0x3F)
        icolor.a = 0.98
        ocolor = RGBA()
        ocolor.r,ocolor.g,ocolor.b = html2rgb(0x1F,0x1F,0x1F)
        ocolor.a = 0.85
        bcolor = RGBA()
        bcolor.r,bcolor.g,bcolor.b = html2rgb(0xCF,0xCF,0xCF)
        bcolor.a = 0.98
        tcolor = RGBA()
        tcolor.r,tcolor.g,tcolor.b = html2rgb(0xEF,0xEF,0xEF)
        tcolor.a = 0.98
        
        entry1 = Entry(w=300,num_lines=3,
                       icolor=icolor,ocolor=ocolor,bcolor=bcolor,tcolor=tcolor)
        entry1.register_change_listener(self)
        self.widgetQ.append(WidgetWrapper(entry1,lpx,lpy))
        
        self.__update_surface()
        
        
            
