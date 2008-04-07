
import random

class WidgetWrapper:
    widget = None
    x = -1
    y = -1
    isKeyActive = True
    
    def __init__(self,widget,x,y,isKeyActive=True):
        self.widget = widget
        self.x = x
        self.y = y
        self.isKeyActive = isKeyActive
        
class Widget:
    id = None
    id_str = None
    w = 0
    h = 0
    
    surface = None
    
    '''
        "clouds" are the parts of other widgets that cloud
        this widget's surface. While responding to the pointer events
    	this widget should not respond to the coordinates that come
    	under these clouds
    '''
    clouds = []
    
    hasFocus = False
    gainedFocus = False
    lostFocus = False
    
    
    def __init__(self,w,h,id=None):
        self.w = w
        self.h = h
        if not id:
            import time
            self.id_str = str(random.randint(1,9999))
            self.id = str(int(time.time()))+'_'+self.id_str
            
        self.surface = None
        self.clouds = []
        
        self.click_listener = None
        self.tap_listener = None
        
        self.__pointer_listener_enabled = True
        
        
    def register_click_listener(self,click_listener):
        self.click_listener = click_listener
        
    def register_tap_listener(self,tap_listener):
        self.tap_listener = tap_listener
        
    def pointer_listener(self,x,y,pressed=False):
        if not self.__pointer_listener_enabled:
            return
        
        oldFocus = self.hasFocus
        
        if x > 0 and x < self.w and y > 0 and y < self.h:
            # Check if we are under any cloud
            for cloud in self.clouds:
            	if x > cloud[0] and x < cloud[2] and y > cloud[1] and y < cloud[3]:
                    self.hasFocus = False
            	    return
            # We are not under any cloud
            self.hasFocus = True
        else:
            self.hasFocus = False
            
        if self.hasFocus:
            if self.tap_listener:
                self.tap_listener(self)
            
        if not oldFocus and self.hasFocus:
            self.gainedFocus = True
            self.lostFocus = False
            if self.click_listener:
                self.click_listener(self)
                
        if oldFocus and not self.hasFocus:
            self.lostFocus = True
            self.gainedFocus = False
                
    def disable_pointer_listener(self):
        self.__pointer_listener_enabled = False
        
    def enable_pointer_listener(self):
        self.__pointer_listener_enabled = True
        
