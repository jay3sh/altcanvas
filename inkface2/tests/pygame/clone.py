
import sys
import os
import pygame
from inkface.pygame import PygameFace, PygameCanvas

class App:
    def main(self):
        self.face = PygameFace(sys.argv[1])

        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0

        self.canvas = PygameCanvas(
            (int(self.face.svg.width),int(self.face.svg.height)),
            flags = flags,
            framerate = 0)

        self.face.clone('newsFlash','newsFlash2',new_x=50,new_y=200)

        self.face.newsFlash2.svg.text = 'Any colorful news?!'

        print 'Updated text: '+self.face.newsFlash2.svg.text
        self.face.newsFlash2.refresh(svg_reload=True)
        
        
        self.canvas.add(self.face)

        self.canvas.paint()

        try:
            self.canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)

App().main()






