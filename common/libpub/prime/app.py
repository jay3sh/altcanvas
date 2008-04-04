
import os 
import cairo
from libpub.prime.widgets.image import Image
from libpub.prime.widgets.pad import Pad 
from libpub.prime.widget import WidgetWrapper
import libpub.prime.mask as mask
from libpub.prime.widgets.fancyentry import FancyEntry 
from libpub.prime.utils import get_image_locations,get_uniform_fit, \
    LAYOUT_STEP, LAYOUT_UNIFORM_OVERLAP,LAYOUT_UNIFORM_SPREAD
from libpub.prime.animation import Path



class WidgetQueue:
    widgetQ = []
    
    def __init__(self):
        pass
    
    def __recalculate_clouds(self):
        '''
            @summary: This method compares surface extents of all existing widgets
                with the new widget and determines if the new widget will
                overlap with them. If it does overlap the existing widgets will 
                loose their isKeyActive and isPoinerActive statuses.
            @param newWidget: New widget being appended to the widgetQ
            
            
    (ox0,oy0)<-------- ow -------->
           ^ ----------------------
           | |                    |
           | |                    |
          oh |                    |
           | |                    |
           v ---------------------- (ox1,oy1)
           
           
                        (nx0,ny0)<-------- nw -------->
                               ^ ----------------------
                               | |                    |
                               | |                    |
                              nh |     newWidget      |
                               | |                    |
                               | |                    |
                               v ---------------------- (nx1,ny1)
        '''
        
        # Cleanup all the clouds before recalculating
        for ww in self.widgetQ:
            ww.widget.clouds = []
            
        for top in range(len(self.widgetQ)):
        
            newWidget = self.widgetQ[top]
            
            for i in range(top):
                ww = self.widgetQ[i]
                ox0 = ww.x
                oy0 = ww.y
                ox1 = ox0 + ww.widget.w
                oy1 = oy0 + ww.widget.h
               
                nx0 = newWidget.x
                ny0 = newWidget.y
                nx1 = nx0 + newWidget.widget.w
                ny1 = ny0 + newWidget.widget.h
                
                if (ox0 < nx0 and ox1 < nx0) or (ox0 > nx1 and ox1 > nx1) or \
                    (oy0 < ny0 and oy1 < ny0) or (oy0 > ny1 and  oy1 > ny1):
                    # There is no overlap
                    continue
                else:
                    '''
                    There is an overlap
                    Calculate the intersection of two widgets' extents
                    and add it to the cloud list of the old widget
                    Also translate them into widget's coordinate system
                    
                    These are top-left and bottom-right vertices of the rectangular
                    intersection of two widgets.
                    '''
                    ww.widget.clouds.append((max(ox0,nx0)-ox0,
                                            max(oy0,ny0)-oy0,
                                            min(ox1,nx1)-ox0,
                                            min(oy1,ny1)-oy0))
    
    def append(self,widgetWrapper):
        self.widgetQ.append(widgetWrapper)
        self.__recalculate_clouds()
        
    def remove(self,widget): 
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                self.widgetQ.remove(ww)
                self.__recalculate_clouds()
                return 
        raise Exception('Widget not found in Queue')
    
    def insert(self,location,widgetWrapper):
        if location < 0:
            self.append(widgetWrapper)
        else:
            self.widgetQ.insert(location,widgetWrapper)
            self.__recalculate_clouds()
    
    def hasWidget(self,widget):
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                return True
        return False
    
    def getWidget(self,widget):
        i = 0
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                return (i,ww)
            i = i+1
        return None

    def next(self):
        for widget in self.widgetQ:
            yield(widget)
            
    def prev(self):
        for i in range(len(self.widgetQ)):
            yield(widgetQ[len(self.widgetQ)-i-1])
            
            
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
    
    class ImageOnPad:
        pass
    
    imageOnPad = None
    
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
            self.widgetQ.append(WidgetWrapper(img,x,y))
            i = i+1

    def __update_surface(self):
        # Create Image widgets for images and lay them out on the surface
        self.ctx.rectangle(0,0,self.app_width,self.app_height)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.fill()
        for ww in self.widgetQ.next():
            self.ctx.set_source_surface(ww.widget.surface,ww.x,ww.y)
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
            
                
    def on_image_click(self,image):
        if not self.inputPad:
            self.inputPad = Pad(int(2*self.app_width/3),int(2*self.app_height/3))
            
        ipx = int(self.app_width/3)-20
        ipy = int(self.app_height/3)-20
        
        if not self.widgetQ.hasWidget(self.inputPad):
            self.widgetQ.append(WidgetWrapper(self.inputPad,ipx,ipy))
            
            
        if self.imageOnPad:
            padOrder,_ = self.widgetQ.getWidget(self.imageOnPad.widget)
        else:
            padOrder = -1
        
        NUM_STEPS = 3 
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
            
            
        
        '''
        entry1 = FancyEntry()
        entry1.register_change_listener(self)
        self.widgetQ.append(WidgetWrapper(entry1,ipx+200,ipy+200))
        '''
        
        self.__update_surface()
        
        