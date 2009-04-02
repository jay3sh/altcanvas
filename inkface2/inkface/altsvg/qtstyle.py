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

from PyQt4.QtGui import QColor, QPen, QBrush, QLinearGradient, QRadialGradient, QMatrix
from PyQt4.QtCore import Qt, QPointF

style_map = {}
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


    def __is_url(self, colorstr):
        ''' simple check '''
        return colorstr.startswith('url')

    def __html2rgb(self, html_color):
        ''' Converts HTML color code to normalized RGB values '''
        try:
            html_color = html_color.lower().replace(' ','')
            if html_color.startswith('rgb'):
                pattern = 'rgb\(([0-9,]+)\)'
                m = re.search(pattern, html_color)
                color_str = m.group(1)
                colors = color_str.split(',')
                r,g,b = map(lambda x: int(float(x)), colors)
                #return (r/256., g/256., b/256.)
                return (r, g, b)
            else:
                # Assume it's a 6 char hex encoded string
                r = int(html_color[1:3], 16)
                g = int(html_color[3:5], 16)
                b = int(html_color[5:7], 16)
                return (r, g, b)
        except Exception, e:
            print 'Error parsing color code [%s]: %s'% (html_color, str(e))
            return (0, 0, 0)

    def _get_pattern_brush(self, pattern_url):
        from inkface.altsvg.style import LinearGradient, RadialGradient
        m = re.search("url\((\S+)\)", pattern_url)
        if m:
            grad_id = m.group(1).replace('#','')
            grad = self.defs[grad_id]
            grad.resolve_href(self.defs)

            if isinstance(grad, LinearGradient):
                if grad.transform_matrix is not None:
                    grad.transform_matrix = QMatrix(*(grad.transform_matrix))
                    pt1 = grad.transform_matrix.map(QPointF(grad.x1, grad.y1))
                    pt2 = grad.transform_matrix.map(QPointF(grad.x2, grad.y2))
                    qgrad = QLinearGradient(pt1.x(), pt1.y(), pt2.x(), pt2.y())
                else:
                    qgrad = QLinearGradient( \
                        grad.x1, grad.y1, grad.x2, grad.y2)
            elif isinstance(grad,RadialGradient):
                # TODO: handle when cx,cy is different than fx,fy

                # Note: I have no clue why inverting the matrix works below
                # found that's how librsvg does it and it works.
                if grad.transform_matrix is not None:
                    print 'Transformed radial gradient not implemented for Qt' 
                    #grad.transform_matrix = QMatrix(*(grad.transform_matrix))
                    #grad.transform_matrix,_ = grad.transform_matrix.inverted()
                    #center = grad.transform_matrix.map(QPointF(grad.fx, grad.fy))
                    #qgrad = QRadialGradient(center.x(), center.y(), grad.r,
                    #                        center.x(), center.y())

                qgrad = QRadialGradient( \
                            grad.fx, grad.fy, grad.r,
                            grad.fx, grad.fy)
                
            stops = []
            for offset, style in grad.stops:
                stop_style = Style(style, None)
                r, g, b = self.__html2rgb(stop_style.stop_color)
                a = 255. * float(stop_style.stop_opacity)
                stops.append((float(offset), QColor(r, g, b, a)))

            qgrad.setStops(stops)

            return QBrush(qgrad)
        

    def get_brush(self):
        r = g = b = 0.
        a = 255.
        if self.__style__.has_key('fill'):
            if self.__style__['fill'] == 'none':
                return None
            elif self.__is_url(self.__style__['fill']):
                brush = self._get_pattern_brush(self.__style__['fill'])
                return brush
            else:
                r, g, b = self.__html2rgb(self.__style__['fill'])

        if self.__style__.has_key('fill-opacity'):
            a = 255. * float(self.__style__['fill-opacity'])

        brush = QBrush()
        brush.setColor(QColor(r, g, b, a))
        brush.setStyle(Qt.SolidPattern)

        return brush
            
    def get_pen(self):
        r = g = b = 0.
        a = 255.
        pen = QPen()
        if self.__style__.has_key('stroke'):
            if self.__style__['stroke'] == 'none':
                return None
            if self.__is_url(self.__style__['stroke']):
                brush = self._get_pattern_brush(self.__style__['stroke'])
                pen.setBrush(brush)
            else:
                r, g, b = self.__html2rgb(self.__style__['stroke'])

                if self.__style__.has_key('stroke-opacity'):
                    a = 255. * float(self.__style__['stroke-opacity'])
 
                pen.setColor(QColor(r, g, b, a))

        if self.__style__.has_key('stroke-width'):
            pen.setWidthF(parse_length(self.__style__['stroke-width']))
        if self.__style__.has_key('stroke-miterlimit'):
            pen.setMiterLimit(
                parse_length(self.__style__['stroke-miterlimit']))
 
        pen.setJoinStyle(Qt.MiterJoin)
        return pen

