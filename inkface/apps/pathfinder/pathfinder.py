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


def hard_coded_path(alpha):
    p_behavior = clutter.BehaviourBspline(alpha=alpha)
    #p_behavior.append_knots((0,100),(100,0),(200,0),(300,100))
    #p_behavior.append_knots((131, 378), (178.0, 297.5), (272.0, 136.5), (319, 56))
    #p_behavior.append_knots((319, 56), (405.25, 104.5), (577.75, 201.5), (664, 250))
    #p_behavior.append_knots((664, 250), (630.75, 291.0), (564.25, 373.0), (531, 414))
    #p_behavior.append_knots((531, 414), (431.0, 405.0), (231.0, 387.0), (131, 378))

    p_behavior.append_knots((100,100))
    p_behavior.append_knots((220,200),(480,200),(600,100))
    p_behavior.append_knots((500,200),(500,300),(600,400))

    p_behavior.append_knots((48,59))
    p_behavior.append_knots((48, 59), (356, 444), (640, 60))
    p_behavior.append_knots((690, 421), (497, 444), (497, 444))
    p_behavior.append_knots((384.75, 347.75), (160.25, 155.25), (48, 59))
    return p_behavior
    

def element_to_bspline(alpha,elem):
    if not elem.d:
        return None
    path = elem.d.replace(',',' ')
    print path
    i = 0
    tokens = path.split()
    print tokens
    xs,ys = (0,0)
    p_behavior = clutter.BehaviourBspline(alpha=alpha)

    while i < len(tokens) and tokens[i].lower() != 'z':
        print "--> "+tokens[i]
        if tokens[i].upper() == 'M':
            print 'moveto '+tokens[i+1]+' '+tokens[i+2]
            xs = int(float(tokens[i+1]))
            ys = int(float(tokens[i+2]))
            p_behavior.append_knots((xs,ys))
            i += 2
        elif tokens[i].upper() == 'L':
            print 'lineto '+tokens[i+1]+' '+tokens[i+2]
            xe = int(float(tokens[i+1]))
            ye = int(float(tokens[i+2]))
            knot = (
                    (xs+(xe-xs)/4.0,ys+(ye-ys)/4.0),
                    (xs+3.0*(xe-xs)/4,ys+3.0*(ye-ys)/4),
                    (xe,ye))

            print knot
            p_behavior.append_knots((xs+(xe-xs)/4.0,ys+(ye-ys)/4.0),
                                    (xs+3.0*(xe-xs)/4,ys+3.0*(ye-ys)/4),
                                    (xe,ye))
            xs,ys = (xe,ye)
            i += 2
        elif tokens[i].upper() == 'C':
            print 'curveto '+str(tokens[i+1:i+7])
            x1 = int(float(tokens[i+1]))
            y1 = int(float(tokens[i+2]))
            x2 = int(float(tokens[i+3]))
            y2 = int(float(tokens[i+4]))
            xe = int(float(tokens[i+5]))
            ye = int(float(tokens[i+6]))
            knot = ((x1,y1),(x2,y2),(xe,ye))
            print knot
            p_behavior.append_knots((x1,y1),(x2,y2),(xe,ye))
            xs,ys = (xe,ye)
            i += 6

        i += 1

    return p_behavior

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
        

        alpha = clutter.Alpha(timeline, clutter.sine_func)

        try:
            p_behavior = element_to_bspline(alpha,self.face.path1)
            #p_behavior = hard_coded_path(alpha)
        except Exception,e:
            import traceback
            print traceback.format_exc()
            return

        '''
        p_behavior = clutter.BehaviourBspline(alpha=alpha)
        knots = ((0,0),(0,150),(250,300),(300,300))
        p_behavior.append_knots(knots)
        p_behavior.append_knots((300,300),(300,350),(350,400),(400,400))
        '''

        p_behavior.apply(self.face.ball_actor)

        #self.face.ball_actor.set_position(0,0)
        self.face.ball_actor.show()
        self.face.path1_actor.show()

        stage.add(self.face.ball_actor)
        stage.add(self.face.path1_actor)
        stage.show()

    
        timeline.start()
        try:
            clutter.main()
        except:
            import traceback
            print traceback.format_exc()
    
        return 0



if __name__ == '__main__':
    sys.exit(PathFinderApp().main())

