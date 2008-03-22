
from math import sqrt

(LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD)  = range(2)


def get_image_locations(count,layout=LAYOUT_UNIFORM_SPREAD,
                        oheight=0,owidth=0):
    '''
        @param count: Number of locations to generate
        @param layout: One of the predefined layouts 
        @param oheight: Hint in terms of Object height that will be placed
            at the returned position. (Optional param)
    '''
    
    max_x = 800
    max_y = 480
        
    if layout == LAYOUT_STEP:
        x = 20
        y = 20
        for i in range(count):
            x = x+75
            y = y+40
            yield (x,y)
            
    elif layout == LAYOUT_UNIFORM_SPREAD:
        if not oheight:
            oheight = 100
            
        if not owidth:
            owidth = 100
            
        avg_space = sqrt(max_x*max_y/count)
        
        max_x_count = int(max_x/avg_space)
        max_y_count = int(count/max_x_count)+1
        
        oh = max_y/max_y_count
        ow = max_x/max_x_count
        
        xc = 0
        yc = 0
        
        for i in range(count):
            xc = i % max_x_count
            yc = i / max_x_count
            x = xc*ow+int((ow-owidth)/2)
            y = yc*oh+int((oh-oheight)/2)
            yield(x,y)
        
