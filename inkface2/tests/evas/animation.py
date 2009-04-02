
import ecore
import sys
from inkface.canvas.ecanvas import ECanvas, EFace

angles = {}

import math
pi2 = math.pi * 2
def get_pos(base_angle, center_x, center_y, w, h):
    t = ecore.time_get()
    t = (t % pi2) - math.pi + base_angle # keep time between -pi and pi
    x = center_x + w * math.cos(t)
    y = center_y + h * math.sin(t)
    return x, y


def get_base_angle(ee, img):
    center_x, center_y = ee.evas.rect.center
    obj_x, obj_y = img.center
    angle = math.atan((center_y-obj_y)/(center_x-obj_x))
    print angle
    return angle


def animate_obj(ee, obj):
    center_x, center_y = ee.evas.rect.center
    w, h = ee.evas.size
    cur_x, cur_y = obj.center
    x, y = get_pos(angles[obj], center_x, center_y, w * 0.3, h * 0.3)
    obj.center = (x, y)
    return True

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))

    face.load_elements(canvas)

    canvas.ee.data['bg'] = face.background

    i = 0
    for obj in (face.obj1, face.obj2, face.obj3):
        obj.image.show()
        x, y = obj.get_position()
        obj.image.move(x, y)

        angles[obj.image] = get_base_angle(canvas.ee, obj.image)

        canvas.ee.data['obj'+str(i)] = obj.image
        ecore.animator_add(animate_obj, canvas.ee, obj.image)

        i+=1 

    ecore.animator_frametime_set(1.0/60.0)

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)
