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



def element_to_bspline(alpha,elem):
    if not elem.d:
        return None
    path = elem.d.replace(',',' ')
    i = 0
    tokens = path.split()
    xs,ys = (0,0)
    p_behavior = clutter.BehaviourBspline(alpha=alpha)

    while i < len(tokens) and tokens[i].lower() != 'z':
        if tokens[i].upper() == 'M':
            xs = int(float(tokens[i+1]))
            ys = int(float(tokens[i+2]))
            p_behavior.append_knots((xs,ys))
            i += 2
        elif tokens[i].upper() == 'L':
            xe = int(float(tokens[i+1]))
            ye = int(float(tokens[i+2]))

            p_behavior.append_knots((xs+(xe-xs)/4.0,ys+(ye-ys)/4.0),
                                    (xs+3.0*(xe-xs)/4,ys+3.0*(ye-ys)/4),
                                    (xe,ye))
            xs,ys = (xe,ye)
            i += 2
        elif tokens[i].upper() == 'C':
            x1 = int(float(tokens[i+1]))
            y1 = int(float(tokens[i+2]))
            x2 = int(float(tokens[i+3]))
            y2 = int(float(tokens[i+4]))
            xe = int(float(tokens[i+5]))
            ye = int(float(tokens[i+6]))
            p_behavior.append_knots((x1,y1),(x2,y2),(xe,ye))
            xs,ys = (xe,ye)
            i += 6

        i += 1

    return p_behavior

class PathFinderApp:
    def __init__(self):
        self.face = ClutterFace(svgname='paths.svg')
        self.paths = [self.face.path0,
                self.face.path1,
                self.face.path2,
                self.face.path3]

        self.pathactors = [self.face.path0_actor,
                self.face.path1_actor,
                self.face.path2_actor,
                self.face.path3_actor]
 
    def on_key_press_event(self,stage, event):
        if event.keyval == clutter.keysyms._0:
            self.refresh_path(0)
        elif event.keyval == clutter.keysyms._1:
            self.refresh_path(1)
        elif event.keyval == clutter.keysyms._2:
            self.refresh_path(2)
        elif event.keyval == clutter.keysyms._3:
            self.refresh_path(3)
        else:
            clutter.main_quit()

    def refresh_path(self,pnum):
        self.stage.remove_all()
        timeline = clutter.Timeline(fps=60, duration=12000)
        timeline.set_loop(True)
        self.alpha = clutter.Alpha(timeline, clutter.sine_func)
        try:
            self.p_behavior = element_to_bspline(self.alpha,self.paths[pnum])
        except Exception,e:
            import traceback
            print traceback.format_exc()
            return

        self.p_behavior.apply(self.face.star_actor)

        self.face.star_actor.show()
        self.pathactors[pnum].show()

        self.stage.add(self.face.star_actor)
        self.stage.add(self.pathactors[pnum])

        self.stage.show()

        timeline.start()

    def main(self):
        self.stage = clutter.Stage()
        self.stage.set_color(
            clutter.Color(red=0xff, green=0xff, blue=0xff, alpha=0xff))
        self.stage.set_size(width=800, height=480)
        self.stage.connect('key-press-event', self.on_key_press_event)
        self.stage.connect('destroy', clutter.main_quit)

        self.refresh_path(0)

        try:
            clutter.main()
        except:
            import traceback
            print traceback.format_exc()
    
        return 0


if __name__ == '__main__':
    sys.exit(PathFinderApp().main())

