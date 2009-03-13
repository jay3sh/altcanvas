
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        self.face = PygameFace('data/gui-4.svg')

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






