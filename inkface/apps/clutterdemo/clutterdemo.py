import sys
import os
from math import pi

import cairo
import clutter
import cluttercairo

import inkface

class Face:
    def __init__(self,svgname,autoload=True):
        assert(os.path.exists(svgname))
        if autoload:
            self.elements = inkface.loadsvg(svgname) 
            for name,elem in self.elements.items():
                self.__dict__[name] = elem

    def __del__(self):
        for name,elem in self.elements.items():
            del self.__dict__[name]
        inkface.unload(self.elements); 

class BehaviourRotate (clutter.Behaviour):
        __gtype_name__ = 'BehaviourRotate'
        def __init__ (self, alpha=None):
                clutter.Behaviour.__init__(self)
                self.set_alpha(alpha)
                self.angle_start = 0.0
                self.angle_end = 359.0

        def do_alpha_notify (self, alpha_value):
                angle = alpha_value \
                      * (self.angle_end - self.angle_start) \
                      / clutter.MAX_ALPHA

                for actor in self.get_actors():
                        actor.set_rotation(clutter.Z_AXIS, angle,
                                           actor.get_x() - 100,
                                           actor.get_y() - 100,
                                           0)


def on_key_press_event (stage, event):
    clutter.main_quit()

class ClutterFace(Face):
    def __init__(self,svgname):
        Face.__init__(self,svgname=svgname)

        for name,elem in self.elements.items():
            actor = cluttercairo.CairoTexture(width=elem.w,height=elem.h)
            ctx = actor.cairo_create()
            ctx.set_source_surface(elem.surface)
            ctx.paint()
            actor.set_position(elem.x,elem.y)
            self.__dict__[name+'_actor'] = actor
            del(ctx)


class Slider(ClutterFace):
    def __init__(self,svgname):
        ClutterFace.__init__(self,svgname=svgname)

        self.motion_handler = None

        self.max_y = self.scale.y+self.scale.h
        self.min_y = self.scale.y

        self.handle_actor.connect('button-press-event',self.on_handle_press)
        self.handle_actor.set_reactive(True)

    def on_handle_press(self,actor, event):
        clutter.grab_pointer(actor)
        self.motion_handler = \
            actor.connect('motion-event',self.on_handle_motion)
        actor.connect('button-release-event',self.on_handle_release)
    
    def on_handle_release(self,actor,event):
        actor.disconnect(self.motion_handler)
        clutter.ungrab_pointer()
    
    def on_handle_motion(self,actor, event):
        ax,ay = actor.get_position()

        if event.y > (self.max_y - actor.get_height()):
            newy = self.max_y - actor.get_height()
        elif event.y < self.min_y:
            newy = self.min_y 
        else:
            newy = event.y

        actor.set_position(ax,newy)
        
class Steering(ClutterFace):
    def __init__(self,svgname):
        ClutterFace.__init__(self,svgname=svgname)


def main ():
    stage = clutter.Stage()
    stage.set_color(clutter.Color(red=0xff, green=0xff, blue=0xff, alpha=0xff))
    stage.set_size(width=800, height=480)
    stage.connect('key-press-event', on_key_press_event)
    stage.connect('destroy', clutter.main_quit)

    slider = Slider('slider.svg')

    stage.add(slider.scalebg_actor)
    slider.scalebg_actor.show()

    stage.add(slider.scale_actor)
    slider.scale_actor.show()

    stage.add(slider.handle_actor)
    slider.handle_actor.show()

    steering = Steering('steering.svg')

    stage.add(steering.steering_actor)
    steering.steering_actor.show()

    stage.show()

    clutter.main()

    return 0

if __name__ == '__main__':
    sys.exit(main())
