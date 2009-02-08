#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# Distributed under GNU General Public License version 3
#

import altsvg
from altsvg.style import *

def draw_rect(ctx, node):
    ''' Render 'rect' SVG element '''
    ctx.save()
    save_x, save_y = ctx.get_current_point()

    style = None

    style_str = node.attrib.get('style')
    if style_str:
        style = load_style(style_str)


    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    w = float(node.attrib.get('width'))
    h = float(node.attrib.get('height'))
    ctx.rel_move_to(x, y)
    ctx.rel_line_to(w, 0)
    ctx.rel_line_to(0, h)
    ctx.rel_line_to(-w, 0)
    ctx.rel_line_to(0, -h)

    if style:
        apply_stroke_style(ctx, style)

    ctx.stroke()

    ctx.move_to(save_x,save_y)
    ctx.restore()

def draw_path(ctx, node):
    ''' Render 'path' SVG element '''
    ctx.save()

    style_str = node.attrib.get('style')
    if style_str:
        style = load_style(style_str)
        if style:
            apply_stroke_style(ctx, style)

    pathdata = node.attrib.get('d')
    pathdata = pathdata.replace(',',' ')

    dx, dy = ctx.get_current_point()

    tokens = pathdata.split()
    i = 0
    while i < len(tokens):
        if tokens[i].isalpha():
            if tokens[i] == 'L':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.line_to(x+dx, y+dy)
                continue
            elif tokens[i] == 'M':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.move_to(x+dx, y+dy)
                continue
            elif tokens[i] == 'C':
                x1 = int(float(tokens[i+1]))
                y1 = int(float(tokens[i+2]))
                x2 = int(float(tokens[i+3]))
                y2 = int(float(tokens[i+4]))
                x = int(float(tokens[i+5]))
                y = int(float(tokens[i+6]))
                i += 7
                ctx.curve_to(x1+dx, y1+dy, x2+dx, y2+dy, x+dx, y+dy)
                continue
            elif tokens[i] == 'z':
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1

    ctx.stroke_preserve()
    ctx.restore()

    
NODE_DRAW_MAP = \
    {
        altsvg.TAG_RECT:draw_rect,
        altsvg.TAG_PATH:draw_path
    }


