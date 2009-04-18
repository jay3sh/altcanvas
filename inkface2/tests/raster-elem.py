

import sys
from inkface.altsvg import VectorDoc

import ecore
import ecore.evas

import pygame
import numpy
from copy import copy


def ARGB2RGBA(surface):
    buf = surface.get_data()
    a = numpy.frombuffer(buf,numpy.uint8)
    a.shape = (surface.get_width(),
                surface.get_height(),4)
    tmp = copy(a[:,:,0])
    a[:,:,0] = a[:,:,2]
    a[:,:,2] = tmp
    return a



class App:
    
    def main(self, svgname):
        vDoc = VectorDoc(svgname)

        elements = vDoc.get_elements()

        pygame.init()

        self.screen = pygame.display.set_mode((320,480),pygame.DOUBLEBUF)
        self.dispsurf = pygame.Surface(self.screen.get_size())
        self.dispsurf.convert()

        egroup = pygame.sprite.LayeredDirty()

        for e in elements:
            w, h = e.surface.get_width(), e.surface.get_height()
            buf = ARGB2RGBA(e.surface)
            i = pygame.image.frombuffer(buf.tostring(),
                        (w, h), "RGBA")

            sprite = pygame.sprite.DirtySprite()
            sprite.image = i
            sprite.rect = i.get_rect()
            sprite.rect.center = (e.x+w/2, e.y+h/2)
            sprite.dirty = True

            egroup.add(sprite)

        egroup.update()
        egroup.draw(self.dispsurf)
        self.screen.blit(self.dispsurf,(0,0))
        pygame.display.flip()

        while True:
            self._handle_event(pygame.event.wait())


        '''
        self.ee = ecore.evas.SoftwareX11(w=320, h=480)

        self.canvas = self.ee.evas


        for e in elements:
            w, h = e.surface.get_width(), e.surface.get_height()
            i = self.canvas.Image()
            i.alpha_set(True)
            i.image_size_set(w, h)
            i.fill_set(0, 0, w, h)
            i.image_data_set(e.surface.get_data())
            i.resize(w, h)

            i.move(e.x, e.y)

            i.show()

        self.ee.show()

        ecore.main_loop_begin()
        '''

    def _handle_event(self,event):
        if event.type == pygame.KEYDOWN:
            sys.exit(0)


if __name__ == '__main__':
    import cProfile
    cProfile.run('App().main(sys.argv[1])',
        sys.argv[1].split('.')[-1]+'.profile')
