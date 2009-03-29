#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# Distributed under GNU General Public License version 3
#

'''
    Rendering routines for individual nodes
'''

from inkface.altsvg.qtstyle import get_style_object
from inkface.altsvg import TAG_RECT, TAG_PATH, \
    TAG_TEXT, TAG_TSPAN, TAG_IMAGE, TAG_HREF

from PyQt4.QtGui import QPainterPath

def draw(painter, path, style):
    pen = style.get_pen()
    if pen is not None:
        painter.strokePath(path, pen)
    brush = style.get_brush()
    if brush is not None:
        painter.fillPath(path, brush)

def draw_rect(painter, node, defs, simulate=False):
    ''' Render 'rect' SVG element '''
    painter.save()
    style = None

    style_str = node.attrib.get('style')
    if style_str:
        style = get_style_object(style_str, defs)

    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    w = float(node.attrib.get('width'))
    h = float(node.attrib.get('height'))

    rx = node.attrib.get('rx')
    ry = node.attrib.get('ry')

    if rx:
        rx = float(rx)
    if ry:
        ry = float(ry)

    path = QPainterPath()

    if rx or ry:
        pass
    else:
        path.addRect(x, y, w, h)

    if simulate:
        bRect = path.boundingRect()
        ex1, ey1, ex2, ey2 = \
            (bRect.left(), bRect.top(), bRect.right(), bRect.bottom())
        try:
            sw = float(style.stroke_width)
        except AttributeError, ae:
            sw = 0
        extents = (ex1-sw, ey1-sw, ex2+sw, ey2+sw)

        painter.restore()
        return extents
    else:
        draw(painter, path, style)

    painter.restore()
 
NODE_DRAW_MAP = \
    {
        TAG_RECT:draw_rect,
    }


