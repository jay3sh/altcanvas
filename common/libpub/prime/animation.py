
from libpub.prime.widget import WidgetWrapper

(LINE,) = range(1)

class Path:
    widget = None
    num_steps = 0
    locus = None
    
    class PathPoint:
        pass
    
    start = None
    stop = None
    
    def __init__(self,widget,num_steps=5,locus=LINE):
        self.widget = widget
        self.num_steps = num_steps 
        self.locus = locus 
    
    def add_start(self,x,y,order):
        self.start = self.PathPoint()
        self.start.x = x
        self.start.y = y
        self.start.order = order
        
    def add_stop(self,x,y,order):
        self.stop = self.PathPoint()
        self.stop.x = x
        self.stop.y = y
        self.stop.order = order
        
    
    def get_widget(self):
        for step in range(self.num_steps):
            nx = self.start.x + int((step+1)*(self.stop.x - self.start.x)/self.num_steps)
            ny = self.start.y + int((step+1)*(self.stop.y - self.start.y)/self.num_steps)
        
            print '%d: %d,%d'%(step,nx,ny)
            yield WidgetWrapper(self.widget,nx,ny)
            
    def get_points(self):
        points = []
        for step in range(self.num_steps):
            nx = self.start.x + int((step+1)*(self.stop.x - self.start.x)/self.num_steps)
            ny = self.start.y + int((step+1)*(self.stop.y - self.start.y)/self.num_steps)
        
            points.append((self.stop.order,WidgetWrapper(self.widget,nx,ny)))
    
        return points