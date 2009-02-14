import altsvg
import pygame
import array
import cairo
import sys
import math
import numpy
from copy import copy

def draw(surface):
    x,y, radius = (250,250, 200)
    ctx = cairo.Context(surface)
    ctx.set_line_width(15)
    ctx.arc(x, y, radius, 0, 2.0 * math.pi)
    ctx.set_source_rgba(1, 1, 0, 1)
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

        self.vectorDoc = altsvg.VectorDoc('data/shape-2.svg')
        self.w,self.h = map(lambda x: int(x), self.vectorDoc.get_doc_props())

        self.window = pygame.display.set_mode((self.w,self.h),pygame.DOUBLEBUF )
        self.screen = pygame.display.get_surface()

        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,self.w,self.h)

        cr = cairo.Context(surface)
        self.vectorDoc.render_full(cr)
        #draw(surface)

        buf = self.rgb_voodo(surface)

        image = pygame.image.frombuffer(buf.tostring(),(self.w,self.h),"RGBA")
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
