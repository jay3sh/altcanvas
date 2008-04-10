
import os 
import cairo
from libpub.prime.widgets.image import Image
from libpub.prime.widgets.pad import Pad 
from libpub.prime.widgets.label import Label 
from libpub.prime.widget import WidgetWrapper
import libpub.prime.mask as mask
from libpub.prime.widgets.fancyentry import FancyEntry 
from libpub.prime.widgets.entry import Entry 
from libpub.prime.utils import get_image_locations,get_uniform_fit, \
    LAYOUT_STEP, LAYOUT_UNIFORM_OVERLAP,LAYOUT_UNIFORM_SPREAD, \
    detect_platform,RGBA,html2rgb,log
from libpub.prime.animation import Path
from libpub.prime.widgetq import WidgetQueue
from libpub.prime.layer import Layer,ImageLayer

            
class App:
    widgetQ = None
    
    surface = None
    ctx = None
    hasChanged = True
    change_listener = None
    
    app_width = 800
    app_height = 480
    
    # Publishr app specific private members
    FOLDER_PATH = None
    images = []
    inputPad = None
    background = None
    bg_ignore_count = 0
    px = 0
    py = 0
    
    class ImageOnPad:
        pass
    
    imageOnPad = None
    labelOnPad = None
    
    def __init__(self,folder_path):                    
        
        self.FOLDER_PATH = folder_path
        
        self.widgetQ = WidgetQueue()
        
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.app_width,self.app_height)
        self.ctx = cairo.Context(self.surface)
        
        LIMIT = 50
        # Get list of images to display
        if os.path.isdir(self.FOLDER_PATH):
            files = os.listdir(self.FOLDER_PATH)
            for f in files:
                if len(self.images) >= LIMIT:
                    break
                
                if f.lower().endswith('jpg') or  \
                    f.lower().endswith('jpeg') or  \
                    f.lower().endswith('xcf') or  \
                    f.lower().endswith('gif'):
                        self.images.append(self.FOLDER_PATH+os.sep+f)

        #self.__load_images()
        self.layers = []
        
        imageLayer = ImageLayer(isVisible=True,images=self.images)
        
        self.layers.append(imageLayer)
        
        
        self.__update_surface()
        
    def __update_surface(self):
        # Create Image widgets for images and lay them out on the surface
        self.ctx.rectangle(0,0,self.app_width,self.app_height)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.fill()
        
        for layer in self.layers:
            layer.draw(self.ctx)
        
        self.hasChanged = True
        if self.change_listener:
            self.change_listener(self)
            
    def get_surface(self):
        self.hasChanged = False
        return self.surface

    def register_change_listener(self,change_listener):
        self.change_listener = change_listener
        
    def dispatch_key_event(self,keyval,state):
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'key_listener'):
                ww.widget.key_listener(keyval,state)
                
    def dispatch_pointer_event(self,x,y,pressed):
        i = 0
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'pointer_listener'):
                ww.widget.pointer_listener(x-ww.x,y-ww.y,pressed)
                i = i+1
                
    def on_surface_change(self,widget):
        self.__update_surface()
            
    def on_background_tap(self,pad):
        # Remove the input pad from widgetQ
        self.bg_ignore_count += 1
        #print 'bg clicked %d,%d'%(self.bg_ignore_count,len(pad.clouds))
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        if self.imageOnPad:
            padOrder,_ = self.widgetQ.getWidget(self.imageOnPad.widget)
            
            ipx = self.px + int(self.app_width/20)
            ipy = self.py + int(self.app_height/3 - self.imageOnPad.widget.h/2)
            pathOut = Path(self.imageOnPad.widget)
            pathOut.add_start(ipx,ipy,padOrder)
            pathOut.add_stop(self.imageOnPad.x,self.imageOnPad.y,self.imageOnPad.order)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
            for i in range(NUM_STEPS):
                if i == 0:
                    continue
                
                if pathOut:
                    self.widgetQ.remove(pathOut.widget)
            
                    (order,ww) = pathOutPoints[i]
                    self.widgetQ.insert(order,ww)
            
            if self.widgetQ.hasWidget(self.labelOnPad):
                self.widgetQ.remove(self.labelOnPad)
                
            # there is no image on input pad now
            self.imageOnPad = None
            self.labelOnPad = None
            
        if self.inputPad and self.widgetQ.hasWidget(self.inputPad):
            self.widgetQ.remove(self.inputPad)
            
        self.__update_surface()
                
    def on_image_click(self,image):
        if not self.inputPad:
            padcolor = RGBA()
            padcolor.r,padcolor.g,padcolor.b = html2rgb(0x0F,0x0F,0x0F)
            padcolor.a = 0.85
            self.inputPad = Pad(int(5*self.app_width/6),int(5*self.app_height/6),
                                color=padcolor,texture=Pad.PLAIN,
                                shape=Pad.ROUNDED_RECT)
            
            log.writeln('InputPad (%s)'%(self.inputPad.id_str))
            
        self.px = int(self.app_width/12)
        self.py = int(self.app_height/12)
        
        if not self.widgetQ.hasWidget(self.inputPad):
            self.widgetQ.append(WidgetWrapper(self.inputPad,self.px,self.py))
            
        # Detect if incoming image is the same one on the pad
        if self.imageOnPad and image.id == self.imageOnPad.widget.id:
            return
        
        if self.imageOnPad:
            padOrder,_ = self.widgetQ.getWidget(self.imageOnPad.widget)
        else:
            padOrder = -1
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        ipx = self.px + int(self.app_width/20)
        ipy = self.py + int(self.app_height/3 - image.h/2)
        
        #inComing
        pathIn = Path(image)
        (orderIn,imageW) = self.widgetQ.getWidget(image)
        pathIn.add_start(imageW.x,imageW.y,orderIn)
        pathIn.add_stop(ipx,ipy,padOrder)
        pathIn.num_steps = NUM_STEPS 
        pathInPoints = pathIn.get_points()
        
        pathOut = None
        #outGoing
        if self.imageOnPad:
            pathOut = Path(self.imageOnPad.widget)
            pathOut.add_start(ipx,ipy,padOrder)
            pathOut.add_stop(self.imageOnPad.x,self.imageOnPad.y,self.imageOnPad.order)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
        for i in range(NUM_STEPS):
            if i == 0:
                continue
            
            # Remove old instances of moving image widgets
            self.widgetQ.remove(pathIn.widget)
            if pathOut:
                self.widgetQ.remove(pathOut.widget)
                
            # Add new instances of moving image widgets
            (order,ww) = pathInPoints[i]
            if padOrder == -1:
                self.widgetQ.append(ww)
                padOrder,_ = self.widgetQ.getWidget(ww.widget)
            else:
                self.widgetQ.insert(padOrder,ww)
                
            if pathOut:
                (order,ww) = pathOutPoints[i]
            	self.widgetQ.insert(order,ww)
        
            # refresh the surface
            self.__update_surface()
            
            
        # Save the imageOnPad
        self.imageOnPad = self.ImageOnPad()
        self.imageOnPad.widget = image
        self.imageOnPad.x = imageW.x
        self.imageOnPad.y = imageW.y
        self.imageOnPad.order = orderIn
            
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
        
        