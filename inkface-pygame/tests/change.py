
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        self.face = PygameFace('data/gui-4.svg')

        self.face.changeButton.onLeftClick = self.change
        
        self.canvas.add(self.face)
        self.canvas.eventloop()

    def change(self):
        self.face.changeText.svg.text = 'This is new text!'
        self.face.changeText.refresh(svg_reload=True)



App().main()






