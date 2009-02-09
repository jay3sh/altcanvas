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
from altsvg.style import \
    load_style, apply_stroke_style, apply_fill_style, \
    has_fill, has_stroke, has_opacity, get_prop

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

    if style and apply_fill_style(ctx, style):
        ctx.fill_preserve()
    else:
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.fill_preserve()


    if style and apply_stroke_style(ctx, style):
        ctx.stroke()
    else:
        ctx.set_source_rgba(0, 0, 0, 0)
        ctx.stroke()


    ctx.move_to(save_x, save_y)
    ctx.restore()

def draw_path(ctx, node):
    ''' Render 'path' SVG element '''
    ctx.save()
    save_x, save_y = ctx.get_current_point()

    style = None
    style_str = node.attrib.get('style')
    if style_str:
        style = load_style(style_str)

    pathdata = node.attrib.get('d')
    pathdata = pathdata.replace(',',' ')

    tokens = pathdata.split()
    i = 0
    while i < len(tokens):
        if tokens[i].isalpha():
            if tokens[i] == 'L':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.line_to(x+save_x, y+save_y)
                continue
            elif tokens[i] == 'M':
                x = int(float(tokens[i+1]))
                y = int(float(tokens[i+2]))
                i += 3
                ctx.move_to(x+save_x, y+save_y)
                continue
            elif tokens[i] == 'C':
                x1 = int(float(tokens[i+1]))
                y1 = int(float(tokens[i+2]))
                x2 = int(float(tokens[i+3]))
                y2 = int(float(tokens[i+4]))
                x = int(float(tokens[i+5]))
                y = int(float(tokens[i+6]))
                i += 7
                ctx.curve_to(x1+save_x, y1+save_y, \
                    x2+save_x, y2+save_y, x+save_x, y+save_y)
                continue
            elif tokens[i] == 'z':
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1

    if has_opacity(style):
        # We need to draw on temporary surface
        ex1, ey1, ex2, ey2 = ctx.stroke_extents()

        # TODO A coarse hack to avoid clipping of curved paths at edges
        #   A hard coded value of 6 is added to the size of surface
        #   This seems to give enough space to accomodate the shape.
        #   Also a fixed offset of 3 is added to translate the context
        #   so that it comes in the middle of tmp surface avoiding clipping
        tmp_surface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32,
                        int(ex2)-int(ex1)+6,int(ey2)-int(ey1)+6)
        tmp_ctx = cairo.Context(tmp_surface)

        # Copy path from original context and use it with tmp context
        path = ctx.copy_path()
        tmp_ctx.translate(-ex1+3,-ey1+3)
        tmp_ctx.append_path(path)

        if style and has_fill(style):
            apply_fill_style(tmp_ctx,style)
            if has_stroke(style):
                tmp_ctx.fill_preserve()
            else:
                tmp_ctx.fill()

        if style and has_stroke(style):
            apply_stroke_style(tmp_ctx,style)
            tmp_ctx.stroke()

        opacity = float(get_prop(style,'opacity'))
        ctx.set_source_surface(tmp_surface,ex1,ey1)
        ctx.paint_with_alpha(opacity)
        ctx.new_path()

    else:
        #
        # We do fill before stroke (the way Inkscape seems to do it)
        # We don't want to reset path data after doing fill,
        # we want to use same path data for stroke as well.
        # Hence, we fill_preserve if there is a stroke to be done
        #
        if style and has_fill(style):
            apply_fill_style(ctx,style)
            if has_stroke(style):
                ctx.fill_preserve()
            else:
                ctx.fill()
    
        if style and has_stroke(style):
            apply_stroke_style(ctx,style)
            ctx.stroke()
    
    ctx.move_to(save_x, save_y)
    ctx.restore()
    
        
NODE_DRAW_MAP = \
    {
        altsvg.TAG_RECT:draw_rect,
        altsvg.TAG_PATH:draw_path
    }


