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

import cairo
import altsvg
from altsvg.style import Style

def draw(ctx, style):
    ''' Generic draw routine '''
    if style.has('opacity') and float(style.opacity) < 1.0:
        # We need to draw on temporary surface
        ex1, ey1, ex2, ey2 = ctx.stroke_extents()

        sw = float(style.stroke_width)

        tmp_surface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32,
                        int(ex2)-int(ex1)+int(2*sw),
                        int(ey2)-int(ey1)+int(2*sw))
        tmp_ctx = cairo.Context(tmp_surface)

        # Copy path from original context and use it with tmp context
        path = ctx.copy_path()
        tmp_ctx.translate(-ex1+int(sw), -ey1+int(sw))
        tmp_ctx.append_path(path)

        if style and style.has('fill'):
            style.apply_fill(tmp_ctx)
            if style.has('stroke'):
                tmp_ctx.fill_preserve()
            else:
                tmp_ctx.fill()

        if style and style.has('stroke'):
            style.apply_stroke(tmp_ctx)
            tmp_ctx.stroke()

        opacity = float(style.opacity)
        ctx.set_source_surface(tmp_surface, ex1, ey1)
        ctx.paint_with_alpha(opacity)
        ctx.new_path()

    else:
        if style and style.has('fill'):
            style.apply_fill(ctx)
            if style.has('stroke'):
                ctx.fill_preserve()
            else:
                ctx.fill()

        if style and style.has('stroke'):
            style.apply_stroke(ctx)
            ctx.stroke()

def draw_rect(ctx, node, defs):
    ''' Render 'rect' SVG element '''
    ctx.save()
    save_x, save_y = ctx.get_current_point()

    style = None

    style_str = node.attrib.get('style')
    if style_str:
        style = Style(style_str, defs)


    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    w = float(node.attrib.get('width'))
    h = float(node.attrib.get('height'))
    ctx.move_to(x, y)
    ctx.line_to(x+w, y)
    ctx.line_to(x+w, y+h)
    ctx.line_to(x, y+h)
    ctx.line_to(x, y)
    ctx.close_path()

    draw(ctx, style)

    ctx.move_to(save_x, save_y)
    ctx.restore()

def draw_path(ctx, node, defs):
    ''' Render 'path' SVG element '''
    ctx.save()

    style = None
    style_str = node.attrib.get('style')
    if style_str:
        style = Style(style_str, defs)

    tokens = node.attrib.get('d').replace(',',' ').split()
    i = 0
    while i < len(tokens):
        if tokens[i].isalpha():
            if tokens[i] == 'L':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.line_to(x, y)
                continue
            elif tokens[i] == 'M':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.move_to(x, y)
                continue
            elif tokens[i] == 'C':
                x1 = int(float(tokens[i+1]))
                y1 = int(float(tokens[i+2]))
                x2 = int(float(tokens[i+3]))
                y2 = int(float(tokens[i+4]))
                x = int(float(tokens[i+5]))
                y = int(float(tokens[i+6]))
                i += 7
                ctx.curve_to(x1, y1, x2, y2, x, y)
                continue
            elif tokens[i] == 'z':
                ctx.close_path()
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1

    draw(ctx, style)
   
    ctx.restore()
    
        
NODE_DRAW_MAP = \
    {
        altsvg.TAG_RECT:draw_rect,
        altsvg.TAG_PATH:draw_path
    }


