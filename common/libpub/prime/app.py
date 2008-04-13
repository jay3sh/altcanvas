
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
    detect_platform,RGBA,html2rgb,log,recalculate_clouds
from libpub.prime.animation import Path
from libpub.prime.widgetq import WidgetQueue
from libpub.prime.layer import Layer,ImageLayer, InputLayer

import libpub
            
class App:
    
    surface = None
    ctx = None
    
    
    app_width = 800
    app_height = 480
    
    def __init__(self):                    
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.app_width,self.app_height)
        self.ctx = cairo.Context(self.surface)
        
        self.layers = []
        
        
        
    def redraw(self):
        # Create Image widgets for images and lay them out on the surface
        self.ctx.rectangle(0,0,self.app_width,self.app_height)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.fill()
        
        for i in range(len(self.layers)):
            self.layers[i].redraw(self.ctx)
        
        
    def adjust_clouds(self):
        widgetQ = []
        print len(widgetQ)
        for layer in self.layers:
            print len(layer.widgetQ.widgetQ)
            widgetQ += layer.widgetQ.widgetQ
        print len(widgetQ)
        print '===='
        recalculate_clouds(widgetQ)


    def dispatch_key_event(self,keyval,state):
        '''
        for ww in self.widgetQ.next():
            if hasattr(ww.widget,'key_listener'):
                ww.widget.key_listener(keyval,state)
        '''
        for layer in self.layers:
            layer.key_listener(x,y,pressed)
                
    def dispatch_pointer_event(self,x,y,pressed):
        for layer in self.layers:
            layer.pointer_listener(x,y,pressed)
                
    def on_surface_change(self,widget):
        #self.update_surface()
        libpub.prime.canvas.redraw()
            
            
            
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
        
        #recalculate_clouds(self.imageLayer.widgetQ.widgetQ)
        self.adjust_clouds()
        
        self.imageLayer.widgetQ.dumpQ('imageLayer')
        
        self.layers.append(self.imageLayer)

        libpub.prime.canvas.redraw()
        
        
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
            
        libpub.prime.canvas.redraw()
                
    def on_image_click(self,image):
            
        if self.inputLayer == None:
            self.inputLayer = InputLayer(app=self,image_dim=(image.w,image.h))
            self.layers.append(self.inputLayer)
            self.inputLayer.widgetQ.dumpQ('inputLayer')
            
        ipx = self.inputLayer.ipx
        ipy = self.inputLayer.ipy
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        #inComing
        pathIn = Path(image)
        imageW = self.imageLayer.get_widget(image)
        if not imageW:
            # This means that this handler got called while
            # another one was already in the middle of an animation
            # and had removed this image widget from the imageLayer queue
            # It is safe to ignore and stop this handler
            return
        pathIn.add_start(imageW.x,imageW.y)
        pathIn.add_stop(ipx,ipy)
        pathIn.num_steps = NUM_STEPS 
        pathInPoints = pathIn.get_points()
        
        pathOut = None
        #outGoing
        if self.inputLayer.imageOnPad:
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy)
            pathOut.add_stop(self.inputLayer.imageOnPad.x,self.inputLayer.imageOnPad.y)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
        # replace the outgoing image with new one
        self.inputLayer.imageOnPad = self.imageLayer.get_widget(image)
            
        for i in range(NUM_STEPS):
            if i == 0:
                # In first step switch the images from their
                # existing layer to the destination layer
                self.imageLayer.remove_widget(pathIn.widget)
                ww = pathInPoints[i]
                self.inputLayer.add_widget(ww)
                
                if pathOut:
                    self.inputLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            elif i == NUM_STEPS-1:
                # In the last step remove the widgets in motion
                # and draw the final layers with their own widget
                # arrangements
                self.inputLayer.remove_widget(pathIn.widget)
                self.inputLayer.show_image()
                
                # TODO: for outgoing widget need to call imageLayers's
                # function
                if pathOut:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            else:
                self.inputLayer.remove_widget(pathIn.widget)
                ww = pathInPoints[i]
                self.inputLayer.add_widget(ww)
                
                if pathOut:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            #recalculate_clouds(self.imageLayer.widgetQ.widgetQ +
            #                   self.inputLayer.widgetQ.widgetQ)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        
        self.inputLayer.hasFocus = True
        
        # refresh the surface
            