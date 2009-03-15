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

from inkface.altsvg.style import Style
from inkface.altsvg import TAG_RECT, TAG_PATH, \
    TAG_TEXT, TAG_TSPAN, TAG_IMAGE, TAG_HREF

def draw(ctx, style):
    ''' Generic draw routine '''
    if style.has('opacity') and float(style.opacity) < 1.0:
        # We need to draw on temporary surface
        ex1, ey1, ex2, ey2 = ctx.stroke_extents()

        sw = float(style.stroke_width)

        tmp_surface = cairo.ImageSurface(
                        cairo.FORMAT_ARGB32,
                        int(ex2-ex1+2*sw),
                        int(ey2-ey1+2*sw))
        tmp_ctx = cairo.Context(tmp_surface)

        # Copy path from original context and use it with tmp context
        path = ctx.copy_path()
        tmp_ctx.translate(-ex1+sw, -ey1+sw)
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
        ctx.set_source_surface(tmp_surface, ex1-sw, ey1-sw)
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

def draw_rect(ctx, node, defs, simulate=False):
    ''' Render 'rect' SVG element '''
    ctx.save()

    style = None

    style_str = node.attrib.get('style')
    if style_str:
        style = Style(style_str, defs)


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

    if rx or ry:
        ctx.move_to(x+rx,y)
        ctx.line_to(x+w-rx,y)
        draw_arc(ctx,rx,ry,0,0,1,x+w,y+ry)
        ctx.line_to(x+w,y+h-ry)
        draw_arc(ctx,rx,ry,0,0,1,x+w-rx,y+h)
        ctx.line_to(x+rx,y+h)
        draw_arc(ctx,rx,ry,0,0,1,x,y+h-ry)
        ctx.line_to(x,y+ry)
        draw_arc(ctx,rx,ry,0,0,1,x+rx,y)
        ctx.close_path()
    else:
        ctx.move_to(x, y)
        ctx.line_to(x+w, y)
        ctx.line_to(x+w, y+h)
        ctx.line_to(x, y+h)
        ctx.line_to(x, y)
        ctx.close_path()

    if simulate:
        ex1, ey1, ex2, ey2 = ctx.stroke_extents()
        try:
            sw = float(style.stroke_width)
        except AttributeError, ae:
            sw = 0
        extents = (ex1-sw, ey1-sw, ex2+sw, ey2+sw)
        ctx.new_path()
        ctx.restore()
        return extents
    else:
        draw(ctx, style)

    ctx.restore()

from math import pi, sin, cos, ceil, fabs, sqrt, atan2

def draw_arc_segment(ctx, xc, yc, th0, th1, rx, ry, xrot):
    sin_th = sin (xrot * (pi/180.0))
    cos_th = cos (xrot * (pi/180.0))

    # inverse transform
    a00 = cos_th * rx
    a01 = -sin_th * ry
    a10 = sin_th * rx
    a11 = cos_th * ry

    th_half = 0.5 * (th1 - th0)
    t = (8.0/3.0) * sin(th_half *0.5) * sin(th_half * 0.5)/sin(th_half)

    x1 = xc + cos(th0) - t * sin(th0)
    y1 = yc + sin(th0) + t * cos(th0)
    x3 = xc + cos(th1)
    y3 = yc + sin(th1)
    x2 = x3 + t * sin(th1)
    y2 = y3 - t * cos(th1)

    ctx.curve_to(
                a00 * x1 + a01 * y1, a10 * x1 + a11 * y1,
                a00 * x2 + a01 * y2, a10 * x2 + a11 * y2,
                a00 * x3 + a01 * y3, a10 * x3 + a11 * y3)

def draw_arc(ctx, rx, ry, xrot, laflag, swflag, x, y):
    if rx == 0.0 or ry == 0.0:
       return

    sin_th = sin (xrot * (pi/180.0))
    cos_th = cos (xrot * (pi/180.0))
    a00 = cos_th / rx
    a01 = sin_th / rx
    a10 = -sin_th / ry
    a11 = cos_th / ry

    cpx, cpy = ctx.get_current_point()
    x0 = a00 * cpx + a01 * cpy
    y0 = a10 * cpx + a11 * cpy
    x1 = a00 * x + a01 * y
    y1 = a10 * x + a11 * y

    d = (x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0)
    sfactor_sq = 1.0 / d - 0.25 # XXX
    if sfactor_sq < 0:
        sfactor_sq = 0

    sfactor = sqrt(sfactor_sq)
    if swflag == laflag:
        sfactor = -sfactor

    xc = 0.5 * (x0 + x1) - sfactor * (y1 - y0)
    yc = 0.5 * (y0 + y1) + sfactor * (x1 - x0)

    th0 = atan2(y0 - yc, x0 - xc)
    th1 = atan2(y1 - yc, x1 - xc)

    th_arc =  th1 - th0

    if th_arc < 0 and swflag:
        th_arc += 2 * pi
    elif th_arc > 0 and not swflag:
        th_arc -= 2 * pi
        
    n_segs = ceil(fabs(th_arc / (pi * 0.5 + 0.001)))

    i = 0
    while i < n_segs:
        draw_arc_segment(ctx, xc, yc,
            th0 + i * th_arc / n_segs,
            th0 + (i+1) * th_arc / n_segs,
            rx, ry, xrot)
        i += 1

    # XXX ctx.set_current_point(x, y)


def draw_tspan(ctx, node, simulate):
    x = float(node.attrib.get('x'))
    y = float(node.attrib.get('y'))
    if simulate:
        xb, yb, w, h, xa, ya = \
            ctx.text_extents(node.text)
        ex1 = x + xb
        ey1 = y + yb
        ex2 = ex1 + w
        ey2 = ey1 + h
        return (ex1, ey1, ex2, ey2)
    else:
        xb, yb, w, h, xa, ya = \
            ctx.text_extents(node.text)
        ctx.move_to(int(x), int(y))
        ctx.show_text(node.text)
    
def draw_text(ctx, node, defs, simulate=False):
    style = None
    style_str = node.attrib.get('style')
    if style_str:
        style = Style(style_str, defs)

    ctx.save()

    tspan_node_list = node.findall(TAG_TSPAN)
    
    extents = (0,0,0,0)
    for tspan_node in tspan_node_list:
        if tspan_node != None:
            style.apply_font(ctx)
            new_extents = draw_tspan(ctx,tspan_node,simulate)
            if simulate:
                extents = _union(extents, new_extents)

    ctx.restore()

    if simulate:
        return extents

# TODO: extent-union dup code
def _union(extents,new_extents):
        if not extents:
            return new_extents

        ox1,oy1,ox2,oy2 = extents
        nx1,ny1,nx2,ny2 = new_extents

        if nx1 < ox1:
            x1 = nx1
        else:
            x1 = ox1

        if ny1 < oy1:
            y1 = ny1
        else:
            y1 = oy1

        if nx2 > ox2:
            x2 = nx2
        else:
            x2 = ox2

        if ny2 > oy2:
            y2 = ny2
        else:
            y2 = oy2

        return (x1, y1, x2, y2)
# TODO: /extent-union dup code

def draw_path(ctx, node, defs, simulate=False):
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
            elif tokens[i] == 'A':
                rx = float(tokens[i+1]) 
                ry = float(tokens[i+2]) 
                xrot = float(tokens[i+3])
                laflag = int(tokens[i+4])
                swflag = int(tokens[i+5])
                x = float(tokens[i+6])
                y = float(tokens[i+7])
                i += 8
                draw_arc(ctx,rx,ry,xrot,laflag,swflag,x,y)
                continue
            elif tokens[i] == 'z':
                ctx.close_path()
                break

        # This should never be reached; 
        # but if the path data is malformed this will help from 
        # getting stuck in an infinite loop
        i += 1

    if simulate:
        ex1, ey1, ex2, ey2 = ctx.stroke_extents()
        try:
            sw = float(style.stroke_width)
        except AttributeError, ae:
            sw = 0
        extents = (ex1-sw, ey1-sw, ex2+sw, ey2+sw)
        ctx.new_path()
        ctx.restore()
        return extents
    else:
        draw(ctx, style)
   
    ctx.restore()
    
def draw_image(ctx, node, defs, simulate=False):
    ''' Render 'image' SVG element '''
    import os
    ctx.save()

    if simulate:
        ex1 = float(node.get('x'))
        ey1 = float(node.get('y'))
        ex2 = ex1 + float(node.get('width'))
        ey2 = ey1 + float(node.get('height'))
        print (ex1,ey1,ex2,ey2)
        return(ex1,ey1,ex2,ey2)


    href = node.get(TAG_HREF)
    if href == None:
        raise Exception("link to image resource absent")

    if not href.lower().endswith('png'):
        raise Exception("Only PNG support is implemented \
                            for embedded images")

    search_path = defs['docpath'].rpartition(os.sep)[0]

    if os.path.exists(href):
        img_path = href
    elif os.path.exists(os.path.join(search_path,href)):
        img_path = os.path.join(search_path,href)
    else:
        raise Exception('Cannot open image '+href)

    # Load the image 
    img_surface = cairo.ImageSurface.create_from_png(img_path)
        
    x = float(node.get('x'))
    y = float(node.get('y'))
    ctx.set_source_surface(img_surface,x,y)

    ctx.paint()
        
    ctx.restore()
        
NODE_DRAW_MAP = \
    {
        TAG_RECT:draw_rect,
        TAG_PATH:draw_path,
        TAG_TEXT:draw_text,
        TAG_IMAGE:draw_image
    }


