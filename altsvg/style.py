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

def load_style(style_str):
    ''' Parse and load style from style string '''
    style = {}
    for style_attr in style_str.strip().split(';'):
        name, value = style_attr.split(':')
        style[name] = value
    return style

def html2rgb(html_color):
    ''' Converts HTML color code to normalized RGB values '''
    r = int(html_color[1:3], 16)
    g = int(html_color[3:5], 16)
    b = int(html_color[5:7], 16)
    return (r/256., g/256., b/256.)

def apply_stroke_style(ctx, style):
    ''' 
    Modify given contex according to the style
        @return True if stroke is specified
                False if stroke is not specified 
    '''
    if style.has_key('stroke'):
        if style['stroke'] == 'none':
            return False
        r, g, b = html2rgb(style['stroke'])
        ctx.set_source_rgb(r, g, b)
    if style.has_key('stroke-width'):
        ctx.set_line_width(float(style['stroke-width']))
    if style.has_key('stroke-miterlimit'):
        ctx.set_miter_limit(float(style['stroke-miterlimit']))
        
    return True

def apply_fill_style(ctx, style):
    ''' 
    Modify given context according to the fill style parameters
    @return True if fill is specified
            False if fill is not specified
    '''
    if style.has_key('fill'):
        if style['fill'] == 'none':
            return False
        r, g, b = html2rgb(style['fill'])
        ctx.set_source_rgb(r, g, b)

    return True

