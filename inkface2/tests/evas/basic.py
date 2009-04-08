
import sys
from inkface.evas import ECanvas, EFace

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)
