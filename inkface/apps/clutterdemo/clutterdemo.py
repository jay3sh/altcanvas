import sys
import os
from math import pi

import cairo
import clutter
import cluttercairo

import inkface

############################################################################
# @class Face 
#   Encapsulation of an SVG file
#   The elements of the SVG file are accessible as attributes of Face object 
############################################################################
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

def on_key_press_event (stage, event):
    clutter.main_quit()

############################################################################
# @class ClutterFace 
#   Derivative of Face - creates Clutter Actors for each element of Face
#   accessible as attributes by name <element_name>+'_actor'
############################################################################
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

############################################################################
# @class Slider
#   Derivative of ClutterFace - Application specific
#   Holds the logic of Slider widget
############################################################################
class Slider(ClutterFace):
    reading_handler = None

    def __init__(self,svgname):
        ClutterFace.__init__(self,svgname=svgname)

        self.MAX_READING = self.scale.y + self.scale.h - self.handle.h/2
        self.MIN_READING = self.scale.y + self.handle.h/2
        self.RANGE = self.MAX_READING - self.MIN_READING
        self.ZERO_READING = self.MIN_READING + self.RANGE/2

        self.motion_handler = None

        self.max_y = self.scale.y+self.scale.h
        self.min_y = self.scale.y

        self.handle_actor.connect('button-press-event',self.on_handle_press)
        self.handle_actor.set_reactive(True)

        ax,ay = self.handle_actor.get_position()
        self.handle_actor.set_position(ax,self.ZERO_READING)

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

        current_reading = newy + self.handle.h/2 -self.MIN_READING

        if self.reading_handler:
            self.reading_handler(current_reading*1./self.RANGE)

        actor.set_position(ax,newy)
        
############################################################################
# @class Steering
#   Derivative of ClutterFace - Application specific
#   Holds the logic of Steering object
############################################################################
class Steering(ClutterFace):
    def __init__(self,svgname):
        ClutterFace.__init__(self,svgname=svgname)

        self.steering_center_x = self.steering.w/2
        self.steering_center_y = self.steering.h/2

    def rotate(self,angle):
        self.steering_actor.set_rotation(clutter.Z_AXIS, angle,
                               self.steering_center_x,
                               self.steering_center_y,
                               0)

############################################################################
# @class Steering
#   Main class that drives the application
############################################################################

class DemoApp:
    def convert_reading_to_rotation(self,percentage_reading):
        angle = int(120 * percentage_reading)
        self.steering.rotate(60-angle)

    def main (self):
        stage = clutter.Stage()
        stage.set_color(
            clutter.Color(red=0xff, green=0xff, blue=0xff, alpha=0xff))
        stage.set_size(width=800, height=480)
        stage.connect('key-press-event', on_key_press_event)
        stage.connect('destroy', clutter.main_quit)
    
        # Load Slider
        self.slider = Slider('slider.svg')
    
        stage.add(self.slider.scalebg_actor)
        self.slider.scalebg_actor.show()
    
        stage.add(self.slider.scale_actor)
        self.slider.scale_actor.show()
    
        stage.add(self.slider.handle_actor)
        self.slider.handle_actor.show()
    
        # Load Steering wheel
        self.steering = Steering('steering.svg')
    
        stage.add(self.steering.steering_actor)
        self.steering.steering_actor.show()
    
        # Register handler to process slider reading and convert it to 
        # steering wheel's rotation
        self.slider.reading_handler = self.convert_reading_to_rotation
    
        stage.show()
    
        clutter.main()
    
        return 0
    
if __name__ == '__main__':
    sys.exit(DemoApp().main())
