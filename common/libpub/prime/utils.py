
from math import sqrt

(LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD,LAYOUT_UNIFORM_OVERLAP)  = range(3)

def get_uniform_fit(count,max_x,max_y,OVERLAP_FACTOR = 1.3):
    total_area = max_x*max_y
    image_area = total_area/count
    image_area = OVERLAP_FACTOR * image_area
    img_side = int(sqrt(image_area))
    return (img_side,img_side)

def get_image_locations(count,layout=LAYOUT_UNIFORM_SPREAD,
                        oheight=0,owidth=0):
    '''
        @param count: Number of locations to generate
        @param layout: One of the predefined layouts 
        @param oheight: Hint in terms of Object height that will be placed
            at the returned position. (Optional param)
        @param owidth: Hint in terms of Object width that will be placed
            at the returned position. (Optional param)
    '''
    
    LEFT_MARGIN_RATIO = 0.1
    TOP_MARGIN_RATIO = 0.1
    
    x_margin = 10
    y_margin = 10
    
    max_x = 800
    max_y = 480
        
    if layout == LAYOUT_STEP:
        x = 20
        y = 20
        for i in range(count):
            x = x+75
            y = y+40
            yield (x,y)
            
    elif layout == LAYOUT_UNIFORM_OVERLAP:
        if not oheight:
            oheight = 100
            
        if not owidth:
            owidth = 100
        
        '''
        The spread of images should be in proportion to the lengths of the
        side of the total area
        
        eqn 1:  x_count * max_y - y_count * max_x = 0
        eqn 2:  x_count * y_count = count
        
        Therefore,
        
        x_count = (count / x_count) * max_x / max_y
        
        x_count = sqrt(count * max_x/max_y)
        
        aspect_ratio = max_x/max_y
        
        x_count = sqrt(count * aspect_ratio)
        
        y_count = count / x_count
        '''
        
        
        cx0 = x_margin + owidth/2
        cy0 = y_margin + oheight/2
        
        cx1 = max_x - (x_margin+owidth/2)
        cy1 = max_y - (y_margin+oheight/2)
        
        aspect_ratio = max_x*1.0/max_y
        x_count = int(sqrt(count * aspect_ratio))
        y_count = int(count / x_count)
        
        for i in range(count):
            xc = i % x_count
            yc = i / x_count
            
            x = cx0 + int(xc*((cx1-cx0)/x_count) - owidth/2)
            y = cy0 + int(yc*((cy1-cy0)/y_count) - oheight/2)
            #x = left_margin + xc * (max_x/x_count)-owidth
            #y = top_margin + yc * (max_y/y_count)-oheight
            #x = xc*ow+int((ow-owidth)/2)
            #y = yc*oh+int((oh-oheight)/2)
            yield(x,y)
        
        
            
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
        
