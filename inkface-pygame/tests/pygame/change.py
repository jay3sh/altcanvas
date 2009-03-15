
import sys
import os
import pygame
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.face = PygameFace(sys.argv[1])
        if os.environ.get('INKFACE_FULLSCREEN') is not None:
            flags = pygame.FULLSCREEN
        else:
            flags = 0
        self.canvas = PygameCanvas(
            (int(self.face.svg.width),int(self.face.svg.height)),
            flags = flags)

        self.face.changeButton.onLeftClick = self.change
        
        self.canvas.add(self.face)
        self.canvas.paint()
        self.canvas.eventloop()

    def change(self, elem):
        self.face.changeText.svg.text = 'This is new text!'
        self.face.changeText.refresh(svg_reload=True)
        self.canvas.paint()
        from time import sleep
        sleep(1)
        import sys
        sys.exit(0)



App().main()






