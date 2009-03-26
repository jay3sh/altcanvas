import pygame
import array
import cairo
import sys
import math
#import _numpy as numpy
from copy import copy
from inkface.altsvg import VectorDoc

import math

    
def draw(surface):
    cr = cairo.Context(surface)

    cr.set_source_rgb(1,0,0)

    ax = 200
    ay = 200
    
    # --------------------------------
    #cr.rectangle(ax,ay,100,100)

    cr.move_to(ax,ay)
    cr.curve_to(ax+30,ay+30,ax+60,ay+30,ax+90,ay)
    cr.curve_to(ax+60,ay-30,ax+30,ay-30,ax,ay)

    #cr.move_to(ax,ay)
    #cr.line_to(ax+200,ay)
    #cr.line_to(ax+200,ay+100)
    #cr.line_to(ax,ay+100)
    #cr.line_to(ax,ay)
    # --------------------------------
    

    ex1,ey1,ex2,ey2 = cr.stroke_extents()
    print cr.stroke_extents()
    cr.stroke()

    #midx,midy = ((ex1+(ex2-ex1)/2),(ey1+(ey2-ey1)/2))
    #orig_vector = (ex1,ey1,midx,midy)
    #orig_vector_mag = math.sqrt((midx-ex1)*(midx-ex1)+(midy-ey1)*(midy-ey1))
    #orig_vector_ang = math.acos((midx-ex1)/orig_vector_mag)

    #print (orig_vector_mag,orig_vector_ang)
    midx,midy = ((ex1+(ex2-ex1)/2),(ey1+(ey2-ey1)/2))
    orig_vector = (ax,ay,midx,midy)
    orig_vector_mag = math.sqrt((midx-ax)*(midx-ax)+(midy-ay)*(midy-ay))
    orig_vector_ang = math.acos((midx-ax)/orig_vector_mag)

    #print (orig_vector_mag,orig_vector_ang)


    mat = cairo.Matrix(0.7071068,-0.7071068,0.7071068,0.7071068,0,0)
    cr.transform(mat)

    mat.invert()

    cmidx,cmidy = mat.transform_point(midx,midy)

    dx = orig_vector_mag * math.cos(orig_vector_ang)
    dy = orig_vector_mag * math.sin(orig_vector_ang)

    cx = cmidx - dx
    cy = cmidy - dy
    
    print (cx,cy)
    
    cr.set_source_rgb(1,1,1)


    # --------------------------------
    #cr.move_to(cx,cy)
    #cr.line_to(cx+200,cy)
    #cr.line_to(cx+200,cy+100)
    #cr.line_to(cx,cy+100)
    #cr.line_to(cx,cy)

    cr.move_to(cx,cy)
    cr.curve_to(cx+30,cy+30,cx+60,cy+30,cx+90,cy)
    cr.curve_to(cx+60,cy-30,cx+30,cy-30,cx,cy)

    #cr.rectangle(cx,cy,100,100)

    # --------------------------------
    nex1,ney1,nex2,ney2 = cr.stroke_extents()
    print (cx-nex1, cy-ney1)
    print cr.stroke_extents()

    
    cx = cx - nex1
    cy = cy - ney1

    cr.move_to(cx,cy)
    cr.curve_to(cx+30,cy+30,cx+60,cy+30,cx+90,cy)
    cr.curve_to(cx+60,cy-30,cx+30,cy-30,cx,cy)

    cr.stroke()
    

    '''
    cr.select_font_face("Bitman Vera Sans",
        cairo.FONT_SLANT_NORMAL,
        cairo.FONT_WEIGHT_BOLD)
    cr.set_font_size(16)

    index = [0, 0xffff, 0x1ffff, -1L, 70,68,76,85,82]
    glyphs = []

    cr.translate(100,100)
    for i in range(9):
        x = 10 * i
        y = 25
        glyph = (index[i], x, y)
        x_bearing, y_bearing, width, height, x_advance, y_advance = \
            cr.glyph_extents((glyph,))

        cr.move_to(x, y)
        cr.set_line_width(1.0)

        cr.rectangle(x+x_bearing-0.5,
                    y+y_bearing-0.5,
                    width+1,
                    height+1)
        
        cr.set_source_rgb(1,0,0)
        cr.stroke()

        cr.set_source_rgb(1,1,1)
        cr.show_glyphs((glyph,))
        
        y = 55
        cr.move_to(x,y)
        cr.glyph_path((glyph,))
        cr.fill()

    '''

    '''
    glyphs = []
    index = 20
    for y in range(5):
        for x in range(5):
            glyphs.append ((index, (x+1)*30, (y+1)*30))
            index += 1
    
    cr.glyph_path (glyphs)
    cr.set_source_rgb (1,1,0)
    cr.fill_preserve ()
    cr.set_source_rgb (1,1,0)
    cr.set_line_width (1.0)
    cr.stroke ()
    '''

    
def draw_shapes(surface):
    xc,yc, radius = (300,300, 50)
    x,y,w,h = (30,30,150,150)
    ctx = cairo.Context(surface)
    ctx.set_line_width(5)

    ctx.move_to(0,0)

    ctx.save()

    ctx.set_matrix(cairo.Matrix(0.5,0,0,1,200,20))

    #ctx.rel_move_to(x, y)
    #ctx.rel_line_to(w, 0)
    #ctx.rel_line_to(0, h)
    #ctx.rel_line_to(-w, 0)
    #ctx.rel_line_to(0, -h)

    ctx.move_to(x, y)
    ctx.line_to(x+w, y)
    ctx.line_to(x+w, y+h)
    ctx.line_to(x, y+h)
    ctx.line_to(x, y)

    ctx.close_path()


    ctx.set_source_rgba(1, 0, 0, 1)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.stroke()
 
    ctx.restore()

    ctx.arc(xc, yc, radius, 0, 2.0 * math.pi)

    ctx.set_source_rgba(1, 0, 0, 1)
    ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 1)
    ctx.stroke()



class App:
    def rgb_voodo(self,surface):
        buf = surface.get_data()
        return buf
        a = numpy.frombuffer(buf,numpy.uint8)
        a.shape = (self.w,self.h,4)
        tmp = copy(a[:,:,0])
        a[:,:,0] = a[:,:,2]
        a[:,:,2] = tmp
        return a
        
    def ARGBtoRGBA(self,str_buf):
        # cairo's ARGB is interpreted by pygame as BGRA due to 
        # then endian-format difference this routine swaps B and R 
        # (0th and 2nd) byte converting it to RGBA format.
        byte_buf = array.array("B", str_buf)
        num_quads = len(byte_buf)/4
        for i in xrange(num_quads):
            tmp = byte_buf[i*4 + 0]
            byte_buf[i*4 + 0] = byte_buf[i*4 + 2]
            byte_buf[i*4 + 2] = tmp
        return byte_buf.tostring()

    def main(self):
        pygame.init()

        self.vectorDoc = VectorDoc(sys.argv[1])

        self.w,self.h = (int(self.vectorDoc.width), int(self.vectorDoc.height))

        self.window = pygame.display.set_mode((self.w,self.h),pygame.DOUBLEBUF )
        self.screen = pygame.display.get_surface()

        #surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)

        data = array.array('B', chr(0) * self.w * self.h * 4)
        stride = self.w * 4
        surface = cairo.ImageSurface.create_for_data(
                    data, cairo.FORMAT_ARGB32,self.w, self.h, stride)

        # Test full rendering
        #cr = cairo.Context(surface)
        #self.vectorDoc.render_full(cr)
        
        #buf = self.ARGBtoRGBA(data)

        # Test custom cairo commands
        draw(surface)
        buf = self.ARGBtoRGBA(data)

        # Test elements interface
        #cr = cairo.Context(surface)
        #elems = self.vectorDoc.get_elements()
        #surface = elems[6].surface

        self.w = surface.get_width()
        self.h = surface.get_height()

        image = pygame.image.frombuffer(buf,(self.w,self.h),"RGBA")
        #image = image.convert()
        self.screen.blit(image, (0,0))
        pygame.display.flip() 

        while True: 
            self.input(pygame.event.wait())

    def input(self,event):
        if event.type == pygame.QUIT or \
            event.type == pygame.KEYDOWN:
            sys.exit(0) 
        
if __name__ == '__main__':
    App().main()
