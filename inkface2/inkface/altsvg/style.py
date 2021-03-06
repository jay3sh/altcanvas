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
import inkface.altsvg

style_map = {}

STYLE_ATTRIBUTES = ('fill', 'stroke', 'stroke-width', 'stroke-dash-array')

def get_style_object(attrib, defs):
    '''
    This method creates a Style object and stores it in a dictionary
    keyed on the style_str. That way next request for parsing same
    string is fulfilled from the dictionary and time spent in parsing
    is saved.
    Repetitive parsing requests for same style string are very common
    hence this strategy helps improve performance.


    As per SVG specs, style attributes can also be direct attributes of 
    a node. Adobe Illustrator seems to follow that. So, if we do not get
    a 'style' attribute in a node, we will search for individual style
    attributes and serialize them into string. Serializing them is important
    because that will caching commonly used styles.
    '''

    if attrib.has_key('style'):
        style_str = attrib.get('style')
    else:
        style_list = []
        for att in STYLE_ATTRIBUTES:
            if attrib.has_key(att):
                style_list.append(att+':'+attrib[att])
        style_str = ';'.join(style_list)

    if style_str in style_map:
        return style_map[style_str]
    else:
        st = Style(style_str, defs)
        style_map[style_str] = st
        return st

def parse_length(value_str):
    if value_str.endswith('px'):
        value_str = value_str.replace('px','')

    return float(value_str)


class Style:
    ''' Class to encapsulate style strings '''
    def __init__(self, style_str, defs):
        ''' Parse and load style from style string '''
        self.__style__ = {}
        self.defs = defs
        if style_str:
            for style_attr in style_str.strip().split(';'):
                if style_attr.strip():
                    name, value = style_attr.split(':')
                    self.__style__[name] = value

    def _is_type_length(self,attr):
        return attr == 'stroke-width' 

    def __getattr__(self, key):
        ''' Override the getter to provide easy access to style attributes '''
        if self.__dict__.has_key(key): 
            return self.__dict__[key]

        modkey = key.replace('_','-')
        if self.__style__.has_key(modkey): 
            val = self.__style__[modkey]
            if self._is_type_length(modkey):
                return parse_length(val)
            else:
                return self.__style__[modkey]
 
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

            if isinstance(grad, LinearGradient):
                if grad.transform_matrix is not None:
                    grad.transform_matrix = cairo.Matrix(*(grad.transform_matrix))
                    grad.x1,grad.y1 = \
                        grad.transform_matrix.transform_point(grad.x1,grad.y1)
                    grad.x2,grad.y2 = \
                        grad.transform_matrix.transform_point(grad.x2,grad.y2)

                cairo_grad = cairo.LinearGradient( \
                    grad.x1, grad.y1, grad.x2, grad.y2)


            elif isinstance(grad,RadialGradient):
                # TODO: handle when cx,cy is different than fx,fy
                cairo_grad = cairo.RadialGradient( \
                    grad.fx, grad.fy, 0,
                    grad.fx, grad.fy, grad.r)
                # Note: I have no clue why inverting the matrix works below
                # found that's how librsvg does it and it works.
                if grad.transform_matrix is not None:
                    grad.transform_matrix = cairo.Matrix(*(grad.transform_matrix))
                    grad.transform_matrix.invert()
                    cairo_grad.set_matrix(grad.transform_matrix)
                    
            for offset, style in grad.stops:
                stop_style = Style(style, None)
                r, g, b = self.__html2rgb(stop_style.stop_color)
                a = float(stop_style.stop_opacity)
                cairo_grad.add_color_stop_rgba(float(offset), r, g, b, a)

            ctx.set_source(cairo_grad)
        
    def __html2rgb(self, html_color):
        ''' Converts HTML color code to normalized RGB values '''
        try:
            html_color = html_color.replace(' ','')
            if html_color.startswith('rgb'):
                pattern = 'rgb\(([0-9,]+)\)'
                m = re.search(pattern, html_color)
                color_str = m.group(1)
                colors = color_str.split(',')
                r,g,b = map(lambda x: int(float(x)), colors)
                return (r/256., g/256., b/256.)
            else:
                # Assume it's a 6 char hex encoded string
                r = int(html_color[1:3], 16)
                g = int(html_color[3:5], 16)
                b = int(html_color[5:7], 16)
                return (r/256., g/256., b/256.)
        except Exception, e:
            print 'Error parsing color code [%s]: %s'% (html_color, str(e))
            return (0, 0, 0)

    def __is_url(self, colorstr):
        ''' simple check '''
        return colorstr.startswith('url')

    def apply_font(self, ctx):

        font_family = None
        font_weight = None
        font_slant = None

        if self.__style__.has_key('font-size'):
            ctx.set_font_size(parse_length(
                                self.__style__['font-size']))

        if self.__style__.has_key('font-family'):
            font_family = self.__style__['font-family']

        if self.__style__.has_key('font-weight'):
            font_weight = {
                'normal':cairo.FONT_WEIGHT_NORMAL,
                'bold'  :cairo.FONT_WEIGHT_BOLD
            }[self.__style__['font-weight']]

        if self.__style__.has_key('font-style'):
            try:
                font_slant = {
                    'normal':cairo.FONT_SLANT_NORMAL,
                    'italic':cairo.FONT_SLANT_ITALIC,
                    'oblique':cairo.FONT_SLANT_OBLIQUE
                }[self.__style__['font-style']]
            except KeyError, ke:
                font_slant = cairo.FONT_SLANT_NORMAL

        r = g = b = 0.0
        a = 1.0
        if self.__style__.has_key('fill'):
            r, g, b = self.__html2rgb(self.__style__['fill'])
            
        if self.__style__.has_key('fill-opacity'):
            a = float(self.__style__['fill-opacity'])

        ctx.set_source_rgba(r, g, b, a)

        if not font_family:
            font_family = "Sans"

        if not font_weight:
            font_weight = cairo.FONT_WEIGHT_NORMAL

        if not font_slant:
            font_slant = cairo.FONT_SLANT_NORMAL

        ctx.select_font_face(font_family, font_slant, font_weight)

    def apply_stroke(self, ctx):
        ''' 
        Modify given context according to the style
            @return True if stroke is specified
                    False if stroke is not specified 
        '''
        if self.__style__.has_key('stroke-width'):
            ctx.set_line_width(parse_length(
                                    self.__style__['stroke-width']))
        if self.__style__.has_key('stroke-miterlimit'):
            ctx.set_miter_limit(float(self.__style__['stroke-miterlimit']))
            
        r = g = b = 0.0
        a = 1.0
        if self.__style__.has_key('stroke'):
            if self.__style__['stroke'] == 'none':
                return False
            if self.__is_url(self.__style__['stroke']):
                self.__apply_pattern(self.__style__['stroke'], ctx)
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
                self.__apply_pattern(self.__style__['fill'], ctx)
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


    def has(self, prop):
        ''' check if prop is present and has active value '''
        return self.__style__.has_key(prop) and \
            self.__style__[prop] != self.__noval[prop]

#
# There are two kinds of Gradient def nodes
# 1. that define stops as their children
# 2. that define position of gradient and have link to first kind
#
# I like to think of later as the instance of former.
#
from inkface.altsvg import TAG_HREF, TAG_STOP

class Gradient:
    ''' Class to encapsulate definition of Gradients '''
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

        transform_str = defnode.get('gradientTransform')

        # TODO: matrix-dup-code
        transform_type = None
        if transform_str is not None:
            transform_str = transform_str.replace(' ','')
            pattern = '(\w+)\s*\(([e0-9-.,]+)\)'
            m = re.search(pattern, transform_str)
            if m: 
                transform_type = m.group(1)
                transform_values = m.group(2)

                if transform_type == 'translate':
                    x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
                elif transform_type == 'matrix':
                    xx, xy, yx, yy, x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
            else:
                raise Exception(
                    'Unable to match transform: %s'%transform_str)

        self.transform_matrix = None

        if transform_type == 'translate':
            self.transform_matrix = (1,0,0,1,x0,y0)
        elif transform_type == 'matrix':
            self.transform_matrix = (xx,xy,yx,yy,x0,y0)

        # TODO: /matrix-dup-code


    def resolve_href(self, defs):
        if self.href:
            self.stops = defs[self.href].stops
        
 
class LinearGradient(Gradient):
    def __init__(self, defnode):
        Gradient.__init__(self, defnode)
        self.x1 = float(defnode.attrib.get('x1', 0))
        self.x2 = float(defnode.attrib.get('x2', 0))
        self.y1 = float(defnode.attrib.get('y1', 0))
        self.y2 = float(defnode.attrib.get('y2', 0))

class RadialGradient(Gradient):
    def __init__(self, defnode):
        Gradient.__init__(self, defnode)
        self.cx = float(defnode.attrib.get('cx', 0))
        self.cy = float(defnode.attrib.get('cy', 0))
        self.fx = float(defnode.attrib.get('fx', 0))
        self.fy = float(defnode.attrib.get('fy', 0))
        self.r = float(defnode.attrib.get('r', 0))
        

