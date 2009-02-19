import altsvg
import pygame
import array
import cairo
import sys
import math
import numpy
from copy import copy

def draw(surface):
    cr = cairo.Context(surface)
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
        a = numpy.frombuffer(buf,numpy.uint8)
        a.shape = (self.w,self.h,4)
        tmp = copy(a[:,:,0])
        a[:,:,0] = a[:,:,2]
        a[:,:,2] = tmp
        return a
        
    def main(self):
        pygame.init()

        self.vectorDoc = altsvg.VectorDoc(sys.argv[1])

        self.w,self.h = (int(self.vectorDoc.width), int(self.vectorDoc.height))

        self.window = pygame.display.set_mode((self.w,self.h),pygame.DOUBLEBUF )
        self.screen = pygame.display.get_surface()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)

        # Test full rendering
        cr = cairo.Context(surface)
        self.vectorDoc.render_full(cr)

        # Test custom cairo commands
        #draw(surface)

        # Test elements interface
        #cr = cairo.Context(surface)
        #elems = self.vectorDoc.get_elements()
        #surface = elems[6].surface

        self.w = surface.get_width()
        self.h = surface.get_height()

        buf = self.rgb_voodo(surface)

        image = pygame.image.frombuffer(buf.tostring(),(self.w,self.h),"RGBA")
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
