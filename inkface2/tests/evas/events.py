
import sys
from inkface.evas import ECanvas, EFace

def handleOk(elem):
    print 'Handling OK'

def handleCancel(elem):
    print 'handling cancel'

def handleYellow(elem):
    print 'handling yellow'

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    face.okButton.onLeftClick = handleOk
    face.cancelButton.onLeftClick = handleCancel
    face.yellowbg.onLeftClick = handleYellow

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)


