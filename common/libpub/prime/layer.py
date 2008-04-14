from libpub.prime.widgetq import WidgetQueue
from libpub.prime.widget import WidgetWrapper

from libpub.prime.utils import * 

from libpub.prime.widgets.pad import Pad
from libpub.prime.widgets.image import Image,PublishrImage 
from libpub.prime.widgets.label import Label 
from libpub.prime.widgets.entry import Entry 
from libpub.prime.widgets.button import Button

from libpub.prime.logic import on_image_click

class Layer:
    
    widgetQ = None
    
    isVisible = False
    
    hasKeyFocus = False
    
    # Yes this will be a generic property
    app_width = 800
    app_height = 480
    
    # This will serve as global access mechanism to top level App object
    App = None
    
    def __init__(self,app,isVisible=True):
        self.App = app
        self.isVisible = isVisible
        
        self.widgetQ = WidgetQueue()
    
    def redraw(self,ctx):
        for ww in self.widgetQ.next():
            ctx.set_source_surface(ww.widget.surface,ww.x,ww.y)
            ctx.paint()
            
    def pointer_listener(self,x,y,pressed):
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'pointer_listener'):
                ww.widget.pointer_listener(x-ww.x,y-ww.y,pressed)
                
    def key_listener(self,key,state):
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'key_listener'):
                ww.widget.key_listener(key,state)
                
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
        Layer.__init__(self, app=app, isVisible=isVisible)
        self.images = images
        
        # Background
        if not self.background:
            
            self.background = Pad(self.app_width,self.app_height, 
                                 texture=Pad.WALLPAPER,shape=Pad.RECT)
            
            self.background.register_tap_listener(self.App.on_background_tap)
            
            log.writeln('BG (%s)'%(self.background.id_str))
            
        self.widgetQ.append(WidgetWrapper(self.background,0,0))
            
        # Images
        imgw,imgh = get_uniform_fit(len(self.images),
                                max_x=self.app_width,max_y=self.app_height)
        i = 0
        
        for (x,y) in get_image_locations(
                len(self.images),layout=LAYOUT_UNIFORM_OVERLAP,
                owidth=imgw,oheight=imgh):
            
            img = PublishrImage(self.images[i],imgw,imgh, 
                        X_MARGIN=int(0.05*imgw),Y_MARGIN=int(0.05*imgh))
            
            log.writeln('%s (%s)'%(img.path,img.id_str))
            
            img.register_click_listener(self.App.on_image_click)
            
            self.widgetQ.append(WidgetWrapper(img,x,y))
            
            i = i+1
            
        # Buttons
        icolor = RGBA()
        icolor.r,icolor.g,icolor.b = html2rgb(0x3F,0x3F,0x3F)
        icolor.a = 1.00
        ocolor = RGBA()
        ocolor.r,ocolor.g,ocolor.b = html2rgb(0x1F,0x1F,0x1F)
        ocolor.a = 0.50
        tcolor = RGBA()
        tcolor.r,tcolor.g,tcolor.b = html2rgb(0xEF,0xEF,0xEF)
        tcolor.a = 0.98
        
        self.importButton = Button(100,35,'Import',fontsize=16,
                                   fontweight=cairo.FONT_WEIGHT_NORMAL,
                                   icolor=icolor,
                                   ocolor=ocolor,
                                   tcolor=tcolor)
        self.widgetQ.append(WidgetWrapper(self.importButton,self.app_width-240,
                                          self.app_height-50))
            
        self.publishButton = Button(100,35,'Publish',fontsize=16,
                                   fontweight=cairo.FONT_WEIGHT_NORMAL,
                                   icolor=icolor,
                                   ocolor=ocolor,
                                   tcolor=tcolor)
        self.widgetQ.append(WidgetWrapper(self.publishButton,self.app_width-120,
                                          self.app_height-50))


class InputLayer(Layer):
    background = None
    imageOnPad = None
    imageLabel = None
    entryDesc = None
    entryTitle = None
    entryTags = None
    
    def __init__(self,app,image_dim=(0,0)):
        Layer.__init__(self, app=app, isVisible=True)
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
            
            
    def save_image_info(self):
        '''
            Saves the fields into the image object that is currently on pad
        '''
        image2save = self.imageOnPad.widget.set_info(
                                            self.entryTitle.text,
                                            self.entryDesc.text,
                                            self.entryTags.text)
        
    def load_image_info(self):
        '''
            Loads the fields from the image object that is currently on pad
        '''
        image2load = self.imageOnPad.widget
        self.entryTitle.text = image2load.title
        self.entryDesc.text = image2load.desc
        self.entryTags.text = image2load.tags

    def show_image(self):
        # Detect if incoming image is the same one on the pad
        self.widgetQ.append(WidgetWrapper(self.imageOnPad.widget,self.ipx,self.ipy))
        
        # Put the name of image on a label below the image
        path = self.imageOnPad.widget.path
        imgName = path[path.rfind('/')+1:path.rfind('.')]
        
        if not self.imageLabel:
            self.imageLabel = Label(imgName,w=self.imageOnPad.widget.h,
                                fontface='Sans Serif',
                                fontweight=cairo.FONT_WEIGHT_BOLD,
                                fontsize=20,
                                color=RGBA(1,1,1,1))
            
            self.widgetQ.append(WidgetWrapper(self.imageLabel,
                                          self.ipx,
                                          self.ipy+self.imageOnPad.widget.h+10))
        else:
            self.imageLabel.text = imgName
            self.imageLabel.redraw()
        
        x_entry = self.px + int(self.app_width/20) + self.imageOnPad.widget.w + \
                        int(self.app_width/20)
                        
        y_title = self.py + 1*self.app_height/12
        y_desc = self.py + 3*self.app_height/12
        y_tags = self.py + 7*self.app_height/12
        
        icolor = RGBA()
        icolor.r,icolor.g,icolor.b = html2rgb(0x3F,0x3F,0x3F)
        icolor.a = 1.00
        ocolor = RGBA()
        ocolor.r,ocolor.g,ocolor.b = html2rgb(0x1F,0x1F,0x1F)
        ocolor.a = 1.00
        bcolor = RGBA()
        bcolor.r,bcolor.g,bcolor.b = html2rgb(0xCF,0xCF,0xCF)
        bcolor.a = 0.98
        tcolor = RGBA()
        tcolor.r,tcolor.g,tcolor.b = html2rgb(0xEF,0xEF,0xEF)
        tcolor.a = 0.98
        
        if not self.entryTitle:
            self.entryTitle = Entry(w=300,num_lines=1,label='Title',
                   icolor=icolor,ocolor=ocolor,bcolor=bcolor,tcolor=tcolor)
            self.widgetQ.append(WidgetWrapper(self.entryTitle,x_entry,y_title))
        
        if not self.entryDesc:
            self.entryDesc = Entry(w=300,num_lines=3,label='Description',
                   icolor=icolor,ocolor=ocolor,bcolor=bcolor,tcolor=tcolor)
            self.widgetQ.append(WidgetWrapper(self.entryDesc,x_entry,y_desc))
        
        if not self.entryTags:
            self.entryTags = Entry(w=300,num_lines=1,label='Tags',
                   icolor=icolor,ocolor=ocolor,bcolor=bcolor,tcolor=tcolor)
            self.widgetQ.append(WidgetWrapper(self.entryTags,x_entry,y_tags))
        
        self.load_image_info()
        
            
