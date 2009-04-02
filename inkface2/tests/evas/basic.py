
import sys
from inkface.canvas.ecanvas import ECanvas, EFace

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    for el in face.elements:
        x, y = el.get_position()
        el.image.move(x, y)
        el.image.show()

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)
