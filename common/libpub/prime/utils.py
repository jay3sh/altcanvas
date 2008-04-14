
import os
import sys
import cairo
from math import sqrt
from math import pi as PI
import random
    
    
class Log:
    def __init__(self):
        self.DEBUG = False 
    
    def write(self,str):
        if self.DEBUG:
            sys.stdout.write(str)
        
    def writeln(self,str):
        if self.DEBUG:
            sys.stdout.write(str+'\n')
            sys.stdout.flush()
    
log = Log()
    
    
class RGBA:
    r = None
    g = None
    b = None
    a = 1.0 
    
    def __init__(self,r=0.0,g=0.0,b=0.0,a=1.0):
        self.r,self.g,self.b,self.a = (r,g,b,a)
        
        
def html2rgb(hr,hg,hb):
    return ((1.0*hr/0xFF),(1.0*hg/0xFF),(1.0*hb/0xFF))
        
        
(LAYOUT_STEP,LAYOUT_UNIFORM_SPREAD,LAYOUT_UNIFORM_OVERLAP)  = range(3)

def get_uniform_fit(count,max_x,max_y,OVERLAP_FACTOR = 0.9):
    if count == 0:
        return (0,0)
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
    
    if count == 0:
        raise Exception('Need non-zero number of images')
    
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
        y_count = int(count / x_count)+1
        
        x_num_gaps = x_count - 1
        y_num_gaps = y_count - 1
            
        for i in range(count):
            xc = i % x_count 
            yc = i / x_count 
            
            x = cx0 + int(xc*((cx1-cx0)/x_num_gaps)) - owidth/2
            y = cy0 + int(yc*((cy1-cy0)/y_num_gaps)) - oheight/2
            
            RANDOM_POS_FACTOR = int(0.2*oheight)
            dx = random.randint(-RANDOM_POS_FACTOR,+RANDOM_POS_FACTOR)
            dy = random.randint(-RANDOM_POS_FACTOR,+RANDOM_POS_FACTOR)
            
            x = x+dx
            y = y+dy
            
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
        
        
(RECT_GRAD_EXPLOSION,RECT_GRAD_SHADOW,RECT_GRAD_TWISTED_SHADOW) = range(3)

def draw_grad_rect(inner=None,outer=None,border=None,
                   type=RECT_GRAD_EXPLOSION,color=RGBA(0,0,0,None)):
    '''
        @param inner: (x,y,w,h) for inner rectangle
        @param outer: (x,y,w,h) for outer rectangle
        @param border: width of the border between inner and outer
    '''
    if not inner and not outer:
        raise Exception('Invalid params')
    
    if (not inner or not outer) and not border:
        raise Exception('Invalid params')
    
    '''
    ix,iy - (x,y) coordinates of four vertices of rectangle in clockwise 
            direction starting from top left
    '''
    
    # @todo: when outer is given
        
    ix = [inner[0],inner[0]+inner[2],inner[0]+inner[2],inner[0]]
    iy = [inner[1],inner[1],inner[1]+inner[3],inner[1]+inner[3]]
    
    bx,by = (
        # EXPLOSION
        ([-1,+1,+1,-1],[-1,-1,+1,+1]),
        
        # SHADOW
        ([+1,+1,+1,+1],[+1,+1,+1,+1]),
        
        # TWISTED SHADOW
        ([-1,-1,+1,+1],[-1,-1,+1,+1])
        
        )[type]
    
    ox = [ix[i]+border*bx[i] for i in range(len(ix))]
    oy = [iy[i]+border*by[i] for i in range(len(iy))]
    
    ow = max(ix)+border
    oh = max(iy)+border
    
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,ow,oh)
    ctx = cairo.Context(surface)
    
    def draw_polygon(ctx,vertices):
        ctx.move_to(vertices[0][0],vertices[0][1])
        for i in range(1,len(vertices)):
            ctx.line_to(vertices[i][0],vertices[i][1])
        ctx.line_to(vertices[0][0],vertices[0][1])

    def make_linear_grad(x0,y0,x1,y1):
        lingrad = cairo.LinearGradient(x0,y0,x1,y1)
        lingrad.add_color_stop_rgba(0,color.r,color.g,color.b,1)
        #lingrad.add_color_stop_rgba(0.1,0,0,0,0.7)
        lingrad.add_color_stop_rgba(1,color.r,color.g,color.b,0)
        return lingrad
    
    # Draw gradients
    # top
    lingrad = make_linear_grad(ix[0],iy[0],ix[0],ox[0])
    draw_polygon(ctx,((ox[0],oy[0]),
            (ix[0],iy[0]),
	        (ix[1],iy[1]),
	        (ox[1],oy[1])))
    
    ctx.set_source(lingrad)
    ctx.fill()
    
    
    # right
    lingrad = make_linear_grad(ix[1],iy[1],ox[1],iy[1])
    draw_polygon(ctx,
            ((ox[1],oy[1]),
             (ox[2],oy[2]),
             (ix[2],iy[2]),
             (ix[1],iy[1])
             ))
    ctx.set_source(lingrad)
    ctx.fill()
    
    # bottom
    lingrad = make_linear_grad(ix[2],iy[2],ix[2],oy[2])
    draw_polygon(ctx,
                 ((ox[2],oy[2]),
                  (ox[3],oy[3]),
                  (ix[3],iy[3]),
                  (ix[2],iy[2])
                  ))
    ctx.set_source(lingrad)
    ctx.fill()
    
    # left
    lingrad = make_linear_grad(ix[3],iy[3],ox[3],iy[3])
    draw_polygon(ctx,
                 ((ox[3],oy[3]),
                  (ox[0],oy[0]),
                  (ix[0],iy[0]),
                  (ix[3],iy[3])
                  ))
    ctx.set_source(lingrad)
    ctx.fill()

    return surface


def detect_platform():
    sin,soe = os.popen4('uname -n')
    line = soe.read()
    if line.lower().find('nokia') >= 0:
        return 'Nokia'
    else:
        return 'Desktop'
    
def show_multiline(w,hi,ctx,text,y_margin):
    # @summary: word by word drawing, center justified
    
    x_offset = 5
    
    used = 0 
    line = 0
    line_text = ''
    _,_,_,_,space_x_adv,_ = ctx.text_extents(str(' '))
    for word in text.split(' '):
    
        x_bearing,y_bearing,width,height,x_adv,y_adv = ctx.text_extents(word)
        
        if( used > 0 and used+width >= w):
            x_b,y_b,wdt,hgt,x_a,y_a = ctx.text_extents(line_text)
            ctx.move_to(x_offset+x_b+int((w-used)/2),line*hi+y_margin-y_b)
            ctx.show_text(line_text)
            line_text = ''
            used = x_offset 
            line += 1
            
        line_text += word+' '
            
        used += x_adv + space_x_adv
        
    # Deal with remaining text
    if line_text != '':
        x_bearing,y_bearing,width,height,x_adv,y_adv = ctx.text_extents(line_text)
        ctx.move_to(x_offset+x_bearing+int((w-used)/2),line*hi+y_margin-y_bearing)
        ctx.show_text(line_text)
    
def recalculate_clouds(widgetQ):
        # Cleanup all the clouds before recalculating
        for ww in widgetQ:
            ww.widget.clouds = []
            
        for top in range(len(widgetQ)):
        
            newWidget = widgetQ[top]
            
            for i in range(top):
                ww = widgetQ[i]
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
                    
def draw_rounded_rect(ctx,x,y,w,h,vr=None):
    x = 0
    y = 0
    x1 = x+w
    y1 = y+h
    
    if not vr:
        vr = int(min(w,h)/10)
    
    ctx.move_to(x+vr,y)
    ctx.line_to(x1-vr,y)
    ctx.arc(x1-vr,y+vr,vr,3*PI/2,0)
    ctx.line_to(x1,y1-vr)
    ctx.arc(x1-vr,y1-vr,vr,0,PI/2)
    ctx.line_to(x+vr,y1)
    ctx.arc(x+vr,y1-vr,vr,PI/2,PI)
    ctx.line_to(x,y+vr)
    ctx.arc(x+vr,y+vr,vr,PI,3*PI/2)
    
    ctx.fill()
    
if __name__ == '__main__':
    print html2rgb(0xFF,0x33,0x33)