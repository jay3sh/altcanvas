#!/usr/bin/python


from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        face = PygameFace('data/gui-10.svg')

        face.xelem.svg.scale(2)
        face.xelem.refresh(svg_reload=True)

        self.canvas.add(face)

        self.canvas.paint()

        self.canvas.eventloop()



App().main()



