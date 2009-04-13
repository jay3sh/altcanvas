
import sys
import evas
from inkface.evas import ECanvas, EFace

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    # A clipper example for future reference.
    #clipper = evas.Rectangle(canvas.canvas, geometry=(10,10,400,400))
    #clipper.show()
    #face.yellowbg.image.clip = clipper

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)
