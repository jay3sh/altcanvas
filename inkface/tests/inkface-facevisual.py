
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

        self.buttonB.onMouseEnter = self.onMouseEnter
        self.buttonB.onMouseLeave = self.onMouseLeave

    def onTap(self,element,elist):
        if not self.Dialog:
            self.Dialog = Dialog(
                self.canvas,svgname='tests/data/overlap-high.svg')
            self.canvas.add(self.Dialog)

    def onMouseEnter(self,element,elist):
        print 'Entering '+element.name

    def onMouseLeave(self,element,elist):
        print 'Leaving '+element.name

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
