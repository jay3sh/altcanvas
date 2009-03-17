
import sys
import os
import pygame
from inkface.canvas.cluttercanvas import ClutterFace, ClutterCanvas

class App:
    def main(self):
        self.face = ClutterFace(sys.argv[1])

        self.canvas = ClutterCanvas(
            (int(self.face.svg.width),int(self.face.svg.height)))

        self.face.clone('newsFlash','newsFlash2',new_x=50,new_y=200)

        self.face.newsFlash2.svg.text = 'Any colorful news?!'

        print 'Updated text: '+self.face.newsFlash2.svg.text
        self.face.newsFlash2.refresh(svg_reload=True)
        
        
        self.canvas.add(self.face)

        try:
            self.canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)

App().main()






