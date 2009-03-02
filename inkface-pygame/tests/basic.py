
import sys
from inkface.canvas import PygameFace, PygameCanvas

face = PygameFace(sys.argv[1])

canvas = PygameCanvas((int(face.svg.width),int(face.svg.height)))

canvas.add(face)

canvas.paint()

canvas.eventloop()
