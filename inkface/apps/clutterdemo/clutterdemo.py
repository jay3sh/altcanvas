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


class Slider:
    def __init__(self,actor,max_y,min_y):
        self.motion_handler = None
        self.actor = actor
        self.max_y = max_y
        self.min_y = min_y
        self.actor.connect('button-press-event',self.on_slider_press)
        self.actor.set_reactive(True)

    def on_slider_press(self,actor, event):
        clutter.grab_pointer(actor)
        self.motion_handler = \
            actor.connect('motion-event',self.on_slider_motion)
        actor.connect('button-release-event',self.on_slider_release)
    
    def on_slider_release(self,actor,event):
        actor.disconnect(self.motion_handler)
        clutter.ungrab_pointer()
    
    def on_slider_motion(self,actor, event):
        ax,ay = actor.get_position()

        if event.y > (self.max_y - self.actor.get_height()):
            newy = self.max_y - self.actor.get_height()
        elif event.y < self.min_y:
            newy = self.min_y 
        else:
            newy = event.y

        actor.set_position(ax,newy)
        

def main ():
    stage = clutter.Stage()
    stage.set_color(clutter.Color(red=0xff, green=0xff, blue=0xff, alpha=0xff))
    stage.set_size(width=800, height=480)
    stage.connect('key-press-event', on_key_press_event)
    stage.connect('destroy', clutter.main_quit)

    #cairo_tex = cluttercairo.CairoTexture(width=800, height=480)
    #cairo_tex.set_position(x=0,y=0)
    #context = cairo_tex.cairo_create()

    elems = inkface.loadsvg('inkface-clutter.svg')

    for name,elem in elems.items():
        elem.user_data = cluttercairo.CairoTexture(width=elem.w, height=elem.h)
        elem.user_data.set_position(elem.x,elem.y)
        ctx = elem.user_data.cairo_create()
        ctx.set_source_surface(elem.surface)
        ctx.paint()
        del(ctx)

    scale = elems['scale'].user_data
    slider = elems['slider'].user_data
    Slider(slider,elems['scale'].y+elems['scale'].h,elems['scale'].y)

    stage.add(scale)
    scale.show()

    stage.add(slider)
    slider.show()


    

    # we scale the context to the size of the surface

    #del(context) # we need to destroy the context so that the
                 # texture gets properly updated with the result
                 # of our operations; you can either move all the
                 # drawing operations into their own function and
                 # let the context go out of scope or you can
                 # explicitly destroy it

    #stage.add(cairo_tex)
    #cairo_tex.show()
    
    '''
    timeline = clutter.Timeline(fps=60, duration=3000)
    timeline.set_loop(True)
    alpha = clutter.Alpha(timeline, clutter.sine_func)

    rbehavior = BehaviourRotate(alpha)
    rbehavior.apply(cairo_tex)
    '''

    stage.show()


    #timeline.start()

    clutter.main()

    return 0

if __name__ == '__main__':
    sys.exit(main())
