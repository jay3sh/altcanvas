#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# Distributed under GNU General Public License version 3
#

'''
    Routines for parsing and loading of SVG style attributes.
'''

import re
import cairo
import altsvg

class Style:
    def __init__(self, style_str, defs):
        ''' Parse and load style from style string '''
        self.__style__ = {}
        self.defs = defs
        if style_str:
            for style_attr in style_str.strip().split(';'):
                if style_attr.strip():
                    name, value = style_attr.split(':')
                    self.__style__[name] = value

    def __getattr__(self, key):
        ''' Override the getter to provide easy access to style attributes '''
        if self.__dict__.has_key(key): return self.__dict__[key]

        modkey = key.replace('_','-')
        if self.__style__.has_key(modkey): return self.__style__[modkey]

        raise AttributeError('Unknown attr '+key)

    def __apply_pattern(self, pattern_url, ctx):
        '''
            TODO: It remains to be implemented when fill-opacity is 
            defined in addition to gradient. It will probably involve 
            rendering the gradient on a temp surface.
        '''
        m = re.search("url\((\S+)\)", pattern_url)
        if m:
            grad_id = m.group(1).replace('#','')
            grad = self.defs[grad_id]
            grad.resolve_href(self.defs)

            if isinstance(grad,LinearGradient):
                cairo_grad = cairo.LinearGradient( \
                    grad.x1,grad.y1,grad.x2,grad.y2)
            elif isinstance(grad,RadialGradient):
                cairo_grad = cairo.RadialGradient( \
                    grad.fx, grad.fy, 0,
                    grad.fx, grad.fy, grad.r)
                    
            for offset,style in grad.stops:
                stop_style = Style(style,None)
                r, g, b = self.__html2rgb(stop_style.stop_color)
                a = float(stop_style.stop_opacity)
                cairo_grad.add_color_stop_rgba(float(offset), r, g, b, a)

            ctx.set_source(cairo_grad)
        
    def __html2rgb(self, html_color):
        ''' Converts HTML color code to normalized RGB values '''
        try:
            r = int(html_color[1:3], 16)
            g = int(html_color[3:5], 16)
            b = int(html_color[5:7], 16)
            return (r/256., g/256., b/256.)
        except Exception, e:
            print 'Error parsing color code [%s]: %s'%(html_color,str(e))
            return (0, 0, 0)

    def __is_url(self,s):
        ''' simple check '''
        return s.startswith('url')

    def apply_stroke(self,ctx):
        ''' 
        Modify given context according to the style
            @return True if stroke is specified
                    False if stroke is not specified 
        '''

        if self.__style__.has_key('stroke-width'):
            ctx.set_line_width(float(self.__style__['stroke-width']))
        if self.__style__.has_key('stroke-miterlimit'):
            ctx.set_miter_limit(float(self.__style__['stroke-miterlimit']))
            
        r = g = b = 0.0
        a = 1.0
        if self.__style__.has_key('stroke'):
            if self.__style__['stroke'] == 'none':
                return False
            if self.__is_url(self.__style__['stroke']):
                self.__apply_pattern(self.__style__['stroke'],ctx)
                return True
            else:
                r, g, b = self.__html2rgb(self.__style__['stroke'])
        if self.__style__.has_key('stroke-opacity'):
            a = float(self.__style__['stroke-opacity'])
    
        ctx.set_source_rgba(r, g, b, a)
    
        return True
    
    def apply_fill(self, ctx):
        ''' 
        Modify given context according to the fill style parameters
        @return True if fill is specified
                False if fill is not specified
        '''
        r = g = b = 0.0
        a = 1.0
        if self.__style__.has_key('fill'):
            if self.__style__['fill'] == 'none':
                return False
            if self.__is_url(self.__style__['fill']):
                self.__apply_pattern(self.__style__['fill'],ctx)
                return True
            else:
                r, g, b = self.__html2rgb(self.__style__['fill'])

        if self.__style__.has_key('fill-opacity'):
            a = float(self.__style__['fill-opacity'])
    
        ctx.set_source_rgba(r, g, b, a)
    
        return True

    __noval = {
                'fill':'none',
                'stroke':'none',
                'opacity':1
            }


    def has(self,prop):
        return self.__style__.has_key(prop) and \
            self.__style__[prop] != self.__noval[prop]

#
# There are two kinds of Gradient def nodes
# 1. that define stops as their children
# 2. that define position of gradient and have link to first kind
#
# I like to think of later as the instance of former.
#
from altsvg import TAG_HREF,TAG_STOP

class Gradient:
    stops = ()
    href = None
    def __init__(self, defnode):
        self.href = defnode.attrib.get(TAG_HREF)
        if self.href: self.href = self.href.replace('#','')
        self.stops = filter( \
            lambda x: x.tag == TAG_STOP, defnode.getchildren())
        self.stops = map ( \
            lambda x: (x.attrib.get('offset'), x.attrib.get('style')),
            self.stops)

    def resolve_href(self, defs):
        if self.href:
            self.stops = defs[self.href].stops
        
 
class LinearGradient(Gradient):
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    def __init__(self, defnode):
        Gradient.__init__(self, defnode)
        self.x1 = float(defnode.attrib.get('x1', 0))
        self.x2 = float(defnode.attrib.get('x2', 0))
        self.y1 = float(defnode.attrib.get('y1', 0))
        self.y2 = float(defnode.attrib.get('y2', 0))

class RadialGradient(Gradient):
    cx = 0
    cy = 0
    fx = 0
    fy = 0
    r = 0
    def __init__(self, defnode):
        Gradient.__init__(self, defnode)
        self.cx = float(defnode.attrib.get('cx', 0))
        self.cy = float(defnode.attrib.get('cy', 0))
        self.fx = float(defnode.attrib.get('fx', 0))
        self.fy = float(defnode.attrib.get('fy', 0))
        self.r = float(defnode.attrib.get('r', 0))
    
        

