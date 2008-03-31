
class Widget:
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
    
    
    def __init__(self,w,h):
        self.w = w
        self.h = h
        self.clouds = []
        
        
    
