
from libpub.prime.widget import WidgetWrapper

(LINE,) = range(1)

class Path:
    widget = None
    total_steps = 0
    locus = None
    start = None
    end = None
    
    def __init__(self,widget,total_steps=5,locus=LINE):
        self.widget = widget
        self.total_steps = total_steps
        self.locus = locus 
    
    def add_start(self,point):
        self.start = point
        
    def add_stop(self,point):
        self.end = point
        
    def get_widget(self):
        for step in range(self.total_steps):
            nx = self.start[0] + \
                int((step+1)*(self.end[0] - self.start[0])/self.total_steps)
            ny = self.start[1] + \
                int((step+1)*(self.end[1] - self.start[1])/self.total_steps)
        
            print '%d: %d,%d'%(step,nx,ny)
            yield WidgetWrapper(self.widget,nx,ny)
            
    def get_points(self):
        points = []
        for step in range(self.total_steps):
            nx = self.start[0] + \
                int((step+1)*(self.end[0] - self.start[0])/self.total_steps)
            ny = self.start[1] + \
                int((step+1)*(self.end[1] - self.start[1])/self.total_steps)
        
            points.append(WidgetWrapper(self.widget,nx,ny))
    
        return points