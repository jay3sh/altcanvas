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

from inkface.altsvg.qtstyle import get_style_object, parse_length
from inkface.altsvg import TAG_RECT, TAG_PATH, \
    TAG_TEXT, TAG_TSPAN, TAG_IMAGE, TAG_HREF

from PyQt4.QtGui import QPainterPath, QPainter

from inkface.altsvg.path import parse_path
from inkface.altsvg.style import parse_length

def draw(painter, path, style):
    pen = style.get_pen()
    if pen is not None:
        painter.strokePath(path, pen)
    brush = style.get_brush()
    if brush is not None:
        painter.fillPath(path, brush)

def draw_path(painter, node, defs, simulate=False):
    painter.save()
    painter.setRenderHint(QPainter.Antialiasing)

    style = get_style_object(node.attrib, defs)
    path_cmds = parse_path(node.get('d'))

    path = QPainterPath()
    for cmd,param in path_cmds:
        if cmd is 'M':
            x, y = param
            path.moveTo(x, y)
            continue
        elif cmd is 'L':
            x, y = param
            path.lineTo(x, y)
            continue
        elif cmd is 'C':
            x1, y1, x2, y2, x3, y3 = param
            path.cubicTo(x1, y1, x2, y2, x3, y3)
            continue
        elif cmd is 'A':
            rx, ry, xrot, laflag, swflag, x, y = param
            #draw_arc(ctx, rx, ry, xrot, laflag, swflag, x, y)
            continue
        elif cmd is 'Z':
            path.closeSubpath()

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

def draw_rect(painter, node, defs, simulate=False):
    ''' Render 'rect' SVG element '''
    painter.save()
    style = None

    style = get_style_object(node.attrib, defs)

    x = parse_length(node.attrib.get('x'))
    y = parse_length(node.attrib.get('y'))
    w = parse_length(node.attrib.get('width'))
    h = parse_length(node.attrib.get('height'))

    rx = node.attrib.get('rx')
    ry = node.attrib.get('ry')

    if rx:
        rx = parse_length(float(rx))
    if ry:
        ry = parse_length(float(ry))

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
        TAG_PATH:draw_path,
    }


