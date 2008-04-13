
import random
from libpub.prime.utils import log

class WidgetQueue:
    widgetQ = []
    
    def __init__(self):
        self.widgetQ = []
        print 'widgetQ ID %d'%random.randint(1,9999)
    
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
    
    def dumpQ(self,op):
        log.write(op+':')
        for ww in self.widgetQ:
            log.write(ww.widget.id_str)
            log.write('-')
            
        log.writeln(' ')
            
    def append(self,widgetWrapper):
        self.widgetQ.append(widgetWrapper)
        #self.__recalculate_clouds()
        self.dumpQ('Append('+widgetWrapper.widget.id_str+
                       ','+str(widgetWrapper.x)+
                       ','+str(widgetWrapper.y)+
                       ')')
        
    def remove(self,widget): 
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                self.widgetQ.remove(ww)
                #self.__recalculate_clouds()
                self.dumpQ('Remove('+ww.widget.id_str+
                       ','+str(ww.x)+
                       ','+str(ww.y)+
                       ')')
                return 
        raise Exception('Widget not found in Queue')
    
    def insert(self,location,widgetWrapper):
        if location < 0:
            self.append(widgetWrapper)
        else:
            self.widgetQ.insert(location,widgetWrapper)
            #self.__recalculate_clouds()
            self.dumpQ('Insert('+
                       widgetWrapper.widget.id_str+
                       ','+str(widgetWrapper.x)+
                       ','+str(widgetWrapper.y)+
                       ')')
    
    def hasWidget(self,widget):
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                return True
        return False
    
    def getWidget(self,widget):
        for ww in self.widgetQ:
            if ww.widget.id == widget.id:
                return ww
        return None

    def next(self):
        for widget in self.widgetQ:
            yield(widget)
            
    def prev(self):
        for i in range(len(self.widgetQ)):
            yield(widgetQ[len(self.widgetQ)-i-1])
            
