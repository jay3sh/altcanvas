
import inkface
import inklib

class Main(inklib.Face):
    Dialog = None
    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)
        self.buttonA.onTap = self.onTap
        self.buttonB.onTap = self.onTap
        self.buttonC.onTap = self.onTap
        self.buttonD.onTap = self.onTap

    def onTap(self,element,elist):
        if not self.Dialog:
            self.Dialog = Dialog(
                self.canvas,svgname='tests/data/overlap-high.svg')
            self.canvas.add(self.Dialog)

class Dialog(inklib.Face):
    def __init__(self,canvas,svgname):
        inklib.Face.__init__(self,canvas,svgname)
        self.bigbutton.onTap = self.onTap

    def onTap(self,element,elist):
        inkface.exit()

def main():
    canvas = inkface.create_X_canvas()
    mainFace = Main(canvas,svgname='tests/data/overlap-low.svg')
    canvas.add(mainFace)

    canvas.eventloop()

if __name__ == '__main__':
    main()
