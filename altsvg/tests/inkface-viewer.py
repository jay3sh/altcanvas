
import sys
import numpy
from copy import copy
import pygame
import altsvg

class App:
    def rgb_voodo(self,surface):
        buf = surface.get_data()
        a = numpy.frombuffer(buf,numpy.uint8)
        a.shape = (surface.get_width(),surface.get_height(),4)
        tmp = copy(a[:,:,0])
        a[:,:,0] = a[:,:,2]
        a[:,:,2] = tmp
        return a
        
    def main(self):
        pygame.init()

        self.vDoc = altsvg.VectorDoc(sys.argv[1])

        self.window = pygame.display.set_mode(
            (int(self.vDoc.width),int(self.vDoc.height)),pygame.DOUBLEBUF )

        self.screen = pygame.display.get_surface()

        elems = self.vDoc.get_elements()

        for e in elems:
            buf = self.rgb_voodo(e.surface)
            image = pygame.image.frombuffer(
                buf.tostring(), 
                (e.surface.get_width(),e.surface.get_height()),
                "RGBA")
            self.screen.blit(image,(e.x,e.y))
            pygame.display.flip()

        while True: 
            self.input(pygame.event.wait())

    def input(self,event):
        if event.type == pygame.QUIT or \
            event.type == pygame.KEYDOWN:
            sys.exit(0) 
 
if __name__ == '__main__':
    App().main()
