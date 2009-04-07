
import sys
from inkface.evas import ECanvas, EFace

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    face.clone('newsFlash', 'newsFlash2', new_x=50, new_y=200)

    face.newsFlash2.svg.text = 'Any colorful news?!'

    print 'Updated text: '+face.newsFlash2.svg.text

    face.newsFlash2.refresh()

    canvas.eventloop()
except KeyboardInterrupt, ki:
    sys.exit(0)
