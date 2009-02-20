
from inkface.canvas import PygameFace, PygameCanvas

face = PygameFace('data/gui-0.svg')

canvas = PygameCanvas((int(face.svg.width),int(face.svg.height)))

canvas.add(face)

canvas.eventloop()
