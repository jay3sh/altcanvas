
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
    
    surface = None
    ctx = None
    hasChanged = True
    change_listener = None
    
    app_width = 800
    app_height = 480
    
    def __init__(self):                    
        
        
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.app_width,self.app_height)
        self.ctx = cairo.Context(self.surface)
        
        #self.__load_images()
        self.layers = []
        
        
        
        
    def update_surface(self):
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
        for layer in self.layers:
            layer.pointer_listener(x,y,pressed)
                
    def on_surface_change(self,widget):
        self.update_surface()
            
            
            
class PublishrApp(App):
    
    FOLDER_PATH = None
    images = []
    inputPad = None
    background = None
    bg_ignore_count = 0
    px = 0
    py = 0
    
    imageLayer = None
    inputLayer = None
    
    def __init__(self,folder_path):
        App.__init__(self)
        self.FOLDER_PATH = folder_path
        
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
                        
        self.imageLayer = ImageLayer(app=self,isVisible=True,images=self.images)
        
        self.layers.append(self.imageLayer)

        self.update_surface()
        
        
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
            
        self.update_surface()
                
    def on_image_click(self,image):
            
        if self.inputLayer == None:
            inputLayer = InputLayer(app=self)
            self.layers.append(inputLayer)
            
        ipx = self.px + int(self.app_width/20)
        ipy = self.py + int(self.app_height/3 - image.h/2)
        
        #inComing
        pathIn = Path(image)
        imageW = self.imageLayer.get_widget(image)
        pathIn.add_start(imageW.x,imageW.y,0)
        pathIn.add_stop(ipx,ipy,0)
        pathIn.num_steps = NUM_STEPS 
        pathInPoints = pathIn.get_points()
        
        pathOut = None
        #outGoing
        if self.inputLayer.imageOnPad:
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy,0)
            pathOut.add_stop(self.imageOnPad.x,self.imageOnPad.y,0)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
        for i in range(NUM_STEPS):
            if i == 0:
                continue
            
            # Remove old instances of moving image widgets
            self.imageLayer.widgetQ.remove(pathIn.widget)
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
            self.update_surface()
            