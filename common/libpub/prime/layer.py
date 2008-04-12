from libpub.prime.widgetq import WidgetQueue
from libpub.prime.widget import WidgetWrapper

from libpub.prime.utils import * 

from libpub.prime.widgets.pad import Pad
from libpub.prime.widgets.image import Image 
from libpub.prime.widgets.label import Label 
from libpub.prime.widgets.entry import Entry 

from libpub.prime.logic import on_image_click

class Layer:
    
    widgetQ = None
    
    isVisible = False
    
    # Yes this will be a generic property
    app_width = 800
    app_height = 480
    
    # This will serve as global access mechanism to top level App object
    App = None
    
    def __init__(self,app,isVisible=True):
        self.App = app
        self.isVisible = isVisible
        
        self.widgetQ = WidgetQueue()
    
    def draw(self,ctx):
        for ww in self.widgetQ.next():
            ctx.set_source_surface(ww.widget.surface,ww.x,ww.y)
            ctx.paint()
            
    def pointer_listener(self,x,y,pressed):
        i = 0
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'pointer_listener'):
                ww.widget.pointer_listener(x-ww.x,y-ww.y,pressed)
                i = i+1
                
    def get_widget(self,widget):
        return self.widgetQ.getWidget(widget)
    
    def remove_widget(self,widget):
        self.widgetQ.remove(widget)
        
    def add_widget(self,widgetW):
        self.widgetQ.append(widgetW)
    
class ImageLayer(Layer):
    # App specific members
    background = None
    images = None
    
    def __init__(self,app,isVisible=True,images=None):
        Layer.__init__(self, app, isVisible)
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
            img.register_click_listener(self.App.on_image_click)
            
            self.widgetQ.append(WidgetWrapper(img,x,y))
            
            i = i+1
            
        print 'ImageLayer l(widgetQ) = %d'%len(self.widgetQ.widgetQ)
            
    def draw(self,ctx):
        #print 'Imagelayer draw - %d'%(len(self.widgetQ.widgetQ))
        Layer.draw(self, ctx)


class InputLayer(Layer):
    background = None
    imageOnPad = None
    imageLabel = None
    
    def __init__(self,app,image_dim=(0,0)):
        Layer.__init__(self, app, isVisible=True)
        padcolor = RGBA()
        padcolor.r,padcolor.g,padcolor.b = html2rgb(0x0F,0x0F,0x0F)
        padcolor.a = 0.85
        self.background = Pad(int(5*self.app_width/6),int(5*self.app_height/6),
                            color=padcolor,texture=Pad.PLAIN,
                            shape=Pad.ROUNDED_RECT)
    
        image_h = image_dim[1]
        self.px = int(self.app_width/12)
        self.py = int(self.app_height/12)
        self.ipx = self.px + int(self.app_width/20)
        self.ipy = self.py + int(self.app_height/3 - image_h/2)
        
        if not self.widgetQ.hasWidget(self.background):
            self.widgetQ.append(WidgetWrapper(self.background,self.px,self.py))
            
        print 'InputLayer l(widgetQ) = %d'%len(self.widgetQ.widgetQ)

    def draw(self,ctx):
        #print 'Inputlayer draw - %d'%(len(self.widgetQ.widgetQ))
        Layer.draw(self, ctx)

    def show_image(self):
        # Detect if incoming image is the same one on the pad
        '''
        if self.imageOnPad and image.id == self.imageOnPad.widget.id:
            return
        '''
        
        self.widgetQ.append(self.imageOnPad)

        
        # Put the name of image on a label below the image
        path = self.imageOnPad.widget.path
        imgName = path[path.rfind('/')+1:path.rfind('.')]
        if self.imageLabel:
            self.widgetQ.remove(self.imageLabel)
            
        self.imageLabel = Label(imgName,w=self.imageOnPad.widget.h,
                                fontface='Sans Serif',
                                fontweight=cairo.FONT_WEIGHT_BOLD,
                                fontsize=20,
                                color=RGBA(1,1,1,1))
            
        self.widgetQ.append(WidgetWrapper(self.imageLabel,
                                          self.ipx,
                                          self.ipy+self.imageOnPad.widget.h+10))
        
        lpx = self.px + int(self.app_width/20) + self.imageOnPad.widget.w + \
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
        
        
        
            
