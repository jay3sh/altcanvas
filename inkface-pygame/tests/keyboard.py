

from inkface.canvas import PygameFace, PygameCanvas


class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        face = PygameFace('data/gui-11.svg')

        face.clone('keyQ','keyQ2x')
        face.keyQ2x.svg.scale(2)
        face.keyQ2x.refresh(svg_reload=True)
        #face.keyQ2x.x = 100
        #face.keyQ2x.y = 100

        self.canvas.add(face)
        self.canvas.paint()
        self.canvas.eventloop()


App().main()
