
import random

class Widget:
    id = None
    w = 0
    h = 0
    '''
        "clouds" are the parts of other widgets that cloud
        this widget's surface. While responding to the pointer events
    	this widget should not respond to the coordinates that come
    	under these clouds
    '''
    clouds = []
    
    hasFocus = False
    # future ideal boundary definition
    enclosure = None
    
    
    def __init__(self,w,h,id=None):
        self.w = w
        self.h = h
        if not id:
            self.id = 'ALTCANVAS_WIDGET_'+str(random.randint(1,9999))
            
        self.clouds = []
        
        
    
