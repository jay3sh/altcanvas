
import unittest


class Face:
    def __init__(self,svgname):
        from inkface.altsvg import VectorDoc
        self.vDoc = VectorDoc(svgname)

        self.elements = self.vDoc.get_elements()
        

class PygameFace(Face):
    def __init__(self,svgname):
        Face.__init__(self,svgname)

        self.mutable_group = pygame.sprite.RenderPlain()
        self.immutable_group = pygame.sprite.RenderPlain()

class Canvas:
    def __init__(self):
        pass

    def __recalculate_clouds(self):
        pass

    def add(self, face):
        pass

    def remove(self, face):
        pass

class PygameCanvas(Canvas):
    def __init__(self,
                resolution = (640,480),
                caption='Inkface App',
                framerate=25):

        Canvas.__init__(self)

        pygame.init()
        screen = pygame.display.set_mode(resolution)
        self.dispsurf = pygame.Surface(screen.get_size())
        pygame.display.set_caption(caption)
        self.clock = pygame.time.clock()
        self.framerate = framerate

    def __painter_thread(self):
        while True:
            self.clock.tick(self.framerate)

    def __handle_event(self,event):
        pass

    def eventloop(self):
        while True:
            self.__handle_event(pygame.event.wait())

    
    
