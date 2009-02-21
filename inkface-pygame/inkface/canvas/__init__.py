
import sys
import unittest
import pygame

class Face:
    def __init__(self,svgname,autoload=True):
        from inkface.altsvg import VectorDoc
        self.svg = VectorDoc(svgname)

        self.elements = self.svg.get_elements()
        
        if autoload:
            for elem in self.elements:
                self.__dict__[elem.id] = elem

class PygameFace(Face):
    sprites = {}

    def ARGBtoRGBA(self,str_buf):
        # cairo's ARGB is interpreted by pygame as BGRA due to 
        # then endian-format difference this routine swaps B and R 
        # (0th and 2nd) byte converting it to RGBA format.
        import array
        byte_buf = array.array("c", str_buf)
        num_quads = len(byte_buf)/4
        for i in xrange(num_quads):
            tmp = byte_buf[i*4 + 0]
            byte_buf[i*4 + 0] = byte_buf[i*4 + 2]
            byte_buf[i*4 + 2] = tmp
        return byte_buf

    def __init__(self,svgname):
        Face.__init__(self,svgname)

        # Create sprites
        for element in self.elements:
            if element.surface:
                self.sprites[element.id] = pygame.sprite.Sprite()
                buf = self.ARGBtoRGBA(element.surface.get_data())
                image = pygame.image.frombuffer(buf.tostring(),
                        (element.surface.get_width(),
                        element.surface.get_height()),"RGBA")
                self.sprites[element.id].image = image
                self.sprites[element.id].rect = image.get_rect()

        # Separate the sprites 
        self.mutable_group = pygame.sprite.RenderPlain()
        self.immutable_group = pygame.sprite.RenderPlain()

        #for element in self.elements:
        #    if element.label != None:
        #        self.mutable_group.add(element.sprite)
        #    else:   
        #        self.immutable_group.add(element.sprite)

class Canvas:
    elementQ = [] 
    def __init__(self):
        pass

    def __recalculate_clouds(self):
        pass

    def add(self, face):
        self.elementQ += face.elements
        pass

    def remove(self, face):
        pass

import threading

class PygameCanvas(Canvas):
    def __init__(self,
                resolution = (640,480),
                caption='Inkface App',
                framerate=25):

        Canvas.__init__(self)

        # TODO check int of resolution

        pygame.init()
        self.screen = pygame.display.set_mode(resolution,pygame.DOUBLEBUF)
        self.dispsurf = pygame.Surface(self.screen.get_size())
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.framerate = framerate

        self.painter = self.PainterThread(self)
        self.painter.start()

    class PainterThread(threading.Thread):
        def __init__(self,canvas):
            threading.Thread.__init__(self)
            self.canvas = canvas

        def run(self):
            while True:
                self.canvas.clock.tick(self.canvas.framerate)
                self.canvas.paint()
        
    def paint(self):
        for elem in self.elementQ:
            sprite = self.sprites[elem.id]
            self.screen.blit(sprite.image,(elem.x,elem.y))

        pygame.display.flip()

    def add(self,face):
        Canvas.add(self,face)
        self.sprites = face.sprites.copy()

    def __handle_event(self,event):
        if event.type == pygame.QUIT:
            sys.exit(0)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            sys.exit(0)

    def eventloop(self):
        while True:
            self.__handle_event(pygame.event.wait())

    
    
