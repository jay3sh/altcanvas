
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
    LAYOUT_STEP, LAYOUT_UNIFORM_OVERLAP,LAYOUT_UNIFORM_SPREAD, open_browser, \
    detect_platform,RGBA,html2rgb,log,recalculate_clouds
from libpub.prime.animation import Path
from libpub.prime.widgetq import WidgetQueue
from libpub.prime.layer import Layer,ImageLayer,InputLayer,FlickrLayer

import libpub
import libpub.flickr_local as flickr
            
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
        for layer in self.layers:
            widgetQ += layer.widgetQ.widgetQ
        recalculate_clouds(widgetQ)

    def dispatch_key_event(self,keyval,state):
        for layer in self.layers:
            layer.key_listener(keyval,state)
                
    def dispatch_pointer_event(self,x,y,pressed):
        for layer in self.layers:
            layer.pointer_listener(x,y,pressed)
                
            
            
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
    flickrLayer = None
    
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
        
        self.adjust_clouds()
        
        self.imageLayer.widgetQ.dumpQ('imageLayer')
        
        self.layers.append(self.imageLayer)

        libpub.prime.canvas.redraw()
        
        # Other initialization
        libpub.start_prime()
        self.flickr = flickr.FlickrObject()
        
        
    def on_background_tap(self,pad):
        # Remove the input pad from widgetQ
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        if self.inputLayer in self.layers:
            
            self.inputLayer.save_image_info()
            
            ipx = self.px + int(self.app_width/20)
            ipy = self.py + int(self.app_height/3 - 
                                self.inputLayer.imageOnPad.widget.h/2)
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy)
            pathOut.add_stop(self.inputLayer.imageOnPad.x,
                             self.inputLayer.imageOnPad.y)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
            for i in range(NUM_STEPS):
                if i == 0:
                    self.inputLayer.remove_widget(pathOut.widget)
            
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                
                    self.inputLayer.imageOnPad = None
                    self.layers.remove(self.inputLayer)
                else:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
                self.adjust_clouds()
                libpub.prime.canvas.redraw()
                
        if self.flickrLayer in self.layers:
            self.layers.remove(self.flickrLayer)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
            
                
    def on_image_click(self,image):
            
        log.writeln('on_image_click - %s'%image.id_str)
        
        if self.inputLayer == None:
            self.inputLayer = InputLayer(app=self,image_dim=(image.w,image.h))
            
        if self.inputLayer not in self.layers:
            self.layers.append(self.inputLayer)
            
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
            self.inputLayer.save_image_info()
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy)
            pathOut.add_stop(self.inputLayer.imageOnPad.x,self.inputLayer.imageOnPad.y)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
        # replace the outgoing image with new one
        self.inputLayer.imageOnPad = self.imageLayer.get_widget(image)
            
        for i in range(NUM_STEPS):
            log.writeln('on_image_click %d'%i)
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
                    
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        
    def on_import_clicked(self,importButton):
        importButton.disable_pointer_listener()
        import gtk
        if detect_platform() == 'Nokia':
            import hildon
            fileChooserDlg = hildon.FileChooserDialog(
                            libpub.prime.canvas,
                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        else:
            fileChooserDlg = gtk.FileChooserDialog('Open picture to publish',
                            libpub.prime.canvas,
                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            
        resp = fileChooserDlg.run()
    
        path = None
        if resp == gtk.RESPONSE_OK:
            path = fileChooserDlg.get_filename()
            
        fileChooserDlg.destroy()
        
        if path:
            images = []
            if os.path.isdir(path):
                files = os.listdir(path)
                for f in files:
                    if f.lower().endswith('jpg') or  \
                        f.lower().endswith('jpeg') or  \
                        f.lower().endswith('gif'):
                            images.append(path+os.sep+f)
            else:
                images.append(path)
            
            self.imageLayer.display_images(images)
            
        importButton.reset_focus()
        importButton.enable_pointer_listener()
        
    def on_quit_clicked(self,widget):
        import gtk
        gtk.main_quit()
    
    def on_publish_clicked(self,widget):
        pass
    
    def on_flickr_clicked(self,widget):
        self.flickrLayer = FlickrLayer(app=self)
        
        if self.flickrLayer not in self.layers:
            self.layers.append(self.flickrLayer)
            
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
            
    authflag = True 
    def on_flickr_authorize(self,widget):
        if self.authflag:
            url = self.flickr.get_authurl()
            if detect_platform() == 'Nokia':
                libpub.prime.canvas.unfullscreen()
            open_browser(widget,url[0])
            self.authflag = False
            
        
        
            