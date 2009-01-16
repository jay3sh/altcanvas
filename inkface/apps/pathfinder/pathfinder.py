#!/usr/bin/python

import sys
import os

import inkface

import clutter
import cluttercairo
import cairo

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



def on_key_press_event (stage, event):
    clutter.main_quit()



class PathFinderApp:
    def __init__(self):
        self.face = ClutterFace(svgname='paths.svg')

    def main(self):
        stage = clutter.Stage()
        stage.set_color(
            clutter.Color(red=0xff, green=0xff, blue=0xff, alpha=0xff))
        stage.set_size(width=800, height=480)
        stage.connect('key-press-event', on_key_press_event)
        stage.connect('destroy', clutter.main_quit)

        timeline = clutter.Timeline(fps=60, duration=6000)
        timeline.set_loop(True)
        
        knots = ((0,0),(0,150),(250,300),(300,300))

        alpha = clutter.Alpha(timeline, clutter.sine_func)

        p_behavior = clutter.BehaviourBspline(alpha=alpha,knots=knots)
        p_behavior.append_knots((300,300),(300,350),(350,400),(400,400))

        p_behavior.apply(self.face.ball_actor)


        self.face.ball_actor.set_position(0,0)
        self.face.ball_actor.show()

        stage.add(self.face.ball_actor)
        stage.show()
    
        timeline.start()
        clutter.main()
    
        return 0



if __name__ == '__main__':
    sys.exit(PathFinderApp().main())

