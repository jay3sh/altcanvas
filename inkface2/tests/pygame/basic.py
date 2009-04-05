
import sys
from inkface.pygame import PygameFace, PygameCanvas

try:
    face = PygameFace(sys.argv[1])

    canvas = PygameCanvas(
        (int(float(face.svg.width)),int(float(face.svg.height))),
        framerate = 0)

    canvas.add(face)

    canvas.paint()

    canvas.eventloop()
except KeyboardInterrupt, ki:
    sys.exit(0)
