
import ecore
import sys
from inkface.evas import ECanvas, EFace

angles = {}
full_size = {}

import math
pi2 = math.pi * 2
def get_pos(base_angle, center_x, center_y, w, h):
    t = ecore.time_get()
    t = (t % pi2) - math.pi + base_angle # keep time between -pi and pi
    x = center_x + w * math.cos(t)
    y = center_y + h * math.sin(t)
    return x, y, t


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
    x, y, t = get_pos(angles[obj], center_x, center_y, w * 0.3, h * 0.3)
    obj.center = (x, y)

    return True

def mouse_in(img, event):
    print 'mouse in '+str(img)+str(event)

def mouse_out(img, event):
    print 'mouse out '+str(img)+str(event)

try:
    face = EFace(sys.argv[1])

    canvas = ECanvas((face.svg.width,face.svg.height))
 
    face.load_elements(canvas)

    #canvas.ee.data['bg'] = face.background

    i = 0
    for obj in (face.obj1, face.obj2, face.obj3):
        #obj.image.show()
        face.clone('obj'+str(i+1),'obj'+str(i+1)+'x2')
        objx2 = face.get('obj'+str(i+1)+'x2')
        objx2.svg.scale(2)
        objx2.refresh()
        #objx2.svg.render()
        obj.image.hide()
        x, y = objx2.get_position()
        objx2.image.move(x, y)

        objx2.image.on_mouse_in_add(mouse_in)

        angles[objx2.image] = get_base_angle(canvas.ee, objx2.image)

        #canvas.ee.data['obj'+str(i)] = obj.image
        ecore.animator_add(animate_obj, canvas.ee, objx2.image)

        i+=1 

    ecore.animator_frametime_set(1.0/60.0)

    canvas.eventloop()

except KeyboardInterrupt, ki:
    sys.exit(0)
