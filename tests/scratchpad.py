
import gtk
import cairo
from math import pi as PI
from math import sqrt

class ScratchApp(gtk.Window):
    da = None
    gc = None
    CANVAS_WIDTH = 800
    CANVAS_HEIGHT = 480
    
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_default_size(self.CANVAS_WIDTH,self.CANVAS_HEIGHT)
        self.da = gtk.DrawingArea()
        self.da.connect('expose_event',self.expose)
        self.da.connect('configure_event',self.configure)
        
        self.da.set_events(gtk.gdk.EXPOSURE_MASK
                       | gtk.gdk.LEAVE_NOTIFY_MASK
                       | gtk.gdk.BUTTON_PRESS_MASK
                       | gtk.gdk.BUTTON_RELEASE_MASK
                       | gtk.gdk.POINTER_MOTION_MASK
                       | gtk.gdk.POINTER_MOTION_HINT_MASK)
    
        self.add(self.da)
        self.show_all()
        
    def configure(self,widget,event):
        _,_,w,h = widget.allocation
        self.pixmap = gtk.gdk.Pixmap(widget.window,w,h)
        w,h = self.pixmap.get_size()
        self.ctx = self.pixmap.cairo_create()
        self.ctx.set_source_rgb(1,1.0*153/256,1.0*51/256)
        self.ctx.rectangle(0,0,w,h)
        self.ctx.fill()
        widget.queue_draw()
        
    def expose(self,widget,event):
        _,_,w,h = widget.allocation
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        
        #
        # Choose HERE which scratch to draw
        #
        self.draw_label(surface)
        
        self.ctx.set_source_surface(surface,w/2,h/2)
        self.ctx.paint()
        
        self.gc = gtk.gdk.GC(widget.window)
        widget.window.draw_drawable(self.gc, self.pixmap, 0,0, 0,0, -1,-1)
    
    def run(self):
        gtk.main()
        
    def draw_label(self,parent_surface):
        
        def get_font_extents(fontface,fontsize):
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,400,200)
            ctx = cairo.Context(surface)
            ctx.set_line_width(6)
            ctx.set_tolerance(.1)
            ctx.select_font_face(fontface)
            ctx.set_font_size(fontsize)
            
            return ctx.font_extents()
        
        w = 100
        x_margin = 10
        y_margin = 10
        
        text = 'spider mobile 2.0'
        fontface = 'sans-serif'
        fontsize = 15
        asc,des,hgt,maxx,maxy = get_font_extents(fontface,fontsize)
        
        text_width = maxx*len(text)
        chars_per_line = int(w/maxx)
        num_lines = int(len(text)/chars_per_line)+1
        h = num_lines * int(hgt+des) + y_margin
        hi = int(hgt+des)
        
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
        ctx = cairo.Context(surface)
        
        ctx.rectangle(0,0,w,h)
        ctx.stroke()
        
        ctx.set_line_width(6)
        ctx.set_tolerance(.1)
        ctx.select_font_face(fontface)
        ctx.set_font_size(fontsize)
        
        used = 0
        line = 0
        for char in text:
            if(used >= w):
                used = 0
                line += 1
                
            x_bearing,y_bearing,width,height,x_adv,y_adv = ctx.text_extents(str(char))
            
            used += width
            ctx.show_text(str(char))
            ctx.move_to(x_margin+x_bearing+used,line*hi+y_margin+(-y_bearing))
                
            
        
        '''# old approach
        
        ctx.set_source_rgb(0,0,0)
        for i in range(num_lines):
            line = text[i*chars_per_line:(i+1)*chars_per_line]
            (x, y, width, height, dx, dy) = ctx.text_extents(line)
            ctx.move_to(x_margin+x,i*hi+y_margin+(-y))
            ctx.show_text(line)        
        '''
        
        parent_ctx = cairo.Context(parent_surface)
        parent_ctx.set_source_surface(surface)
        parent_ctx.paint()
        
        
        
    def draw_round_corner_rect(self,surface):
        w = surface.get_width()
        h = surface.get_height()
        ctx = cairo.Context(surface)
        
        ctx.set_source_rgba(0.2,0.2,0.2,1)
        
        x0 = 100
        y0 = 100
        x1 = w-200
        y1 = h-200
        
        vr = 20
        
        ctx.move_to(x0+vr,y0)
        ctx.line_to(x1-vr,y0)
        ctx.arc(x1-vr,y0+vr,vr,3*PI/2,0)
        ctx.line_to(x1,y1-vr)
        ctx.arc(x1-vr,y1-vr,vr,0,PI/2)
        ctx.line_to(x0+vr,y1)
        ctx.arc(x0+vr,y1-vr,vr,PI/2,PI)
        ctx.line_to(x0,y0+vr)
        ctx.arc(x0+vr,y0+vr,vr,PI,3*PI/2)
        
        #ctx.rectangle(100,100,w-200,h-200)
        ctx.fill()
        
    def draw_grad_rect(self,surface):
        self.draw_grad_rect_inner(surface, 
                       inner = (100,100,300,300),
                       border = 20)
        
    def draw_grad_rect_inner(self,surface,inner=None,outer=None,border=None):
        '''
            @param inner: (x,y,w,h) for inner rectangle
            @param outer: (x,y,w,h) for outer rectangle
            @param border: width of the border between inner and outer
        '''
        if not inner and not outer:
            raise Exception('Invalid params')
        
        if (not inner or not outer) and not border:
            raise Exception('Invalid params')
        
        ix = [inner[0],inner[0]+inner[2],inner[0]+inner[2],inner[0]]
        iy = [inner[1],inner[1],inner[1]+inner[3],inner[1]+inner[3]]
        
        type = 0
        
        bx,by = (
            # EXPLOSION
            ([-1,+1,+1,-1],[-1,-1,+1,+1]),
            
            # SHADOW
            ([+1,+1,+1,+1],[+1,+1,+1,+1]),
            
            # TWISTED SHADOW
            ([-1,-1,+1,+1],[-1,-1,+1,+1])
            
            )[type]
        
        # EXPLOSION
        #bx = [-1,+1,+1,-1]
        #by = [-1,-1,+1,+1]
        
        # TWISTED SHADOW
        # bx = [-1,-1,+1,+1]
        # by = [-1,-1,+1,+1]
        
        # SHADOW
        # bx = [+1,+1,+1,+1]
        # by = [+1,+1,+1,+1]
        
        ox = [ix[i]+border*bx[i] for i in range(len(ix))]
        oy = [iy[i]+border*by[i] for i in range(len(iy))]
        
        # TWISTED SHADOW
        #ox = [elem-border for elem in ix[0:2]]+[elem+border for elem in ix[2:4]]
        #oy = [elem-border for elem in iy[0:2]]+[elem+border for elem in iy[2:4]]
        
        # SHADOW
        #ox = [elem+border for elem in ix]
        #oy = [elem+border for elem in iy]
        
        ctx = cairo.Context(surface)
        
        def draw_polygon(ctx,vertices):
            ctx.move_to(vertices[0][0],vertices[0][1])
            for i in range(1,len(vertices)):
                ctx.line_to(vertices[i][0],vertices[i][1])
            ctx.line_to(vertices[0][0],vertices[0][1])

        def make_linear_grad(x0,y0,x1,y1):
            lingrad = cairo.LinearGradient(x0,y0,x1,y1)
            lingrad.add_color_stop_rgba(0,0,0,0,1)
            #lingrad.add_color_stop_rgba(0.1,0,0,0,0.7)
            lingrad.add_color_stop_rgba(1,0,0,0,0)
            return lingrad
        
        # Draw gradients
        # top
        lingrad = make_linear_grad(ix[0],iy[0],ix[0],ox[0])
        draw_polygon(ctx,
                ((ox[0],oy[0]),
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
        
    def draw_scratch(self,surface):
        w = surface.get_width()
        h = surface.get_height()
        ctx = cairo.Context(surface)
        r = sqrt(w*w+h*h)
        grad = cairo.RadialGradient(0,0,0,0,0,r+100)
        grad.add_color_stop_rgba(0,0,0,0,1)
        grad.add_color_stop_rgba(0.75,0,0,0,0.15)
        grad.add_color_stop_rgba(1,0,0,0,0)
        
        #arc = ctx.arc(int(w/4),int(h/3),30,0,2*PI)
        rect = ctx.rectangle(0,0,w,h)
        ctx.set_source(grad)
        ctx.fill()
        
        '''
        rect = ctx.rectangle(10,10,w-20,h-20)
        ctx.set_source(lingrad)
        ctx.fill()
        '''

if __name__ == '__main__':
    ScratchApp().run()