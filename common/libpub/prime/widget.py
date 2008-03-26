
class Widget:
    # Temporary traditional boundary definitions
    x = 0
    y = 0
    w = 0
    h = 0
    hasFocus = False
    # future ideal boundary definition
    enclosure = None
    
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        
        
    
