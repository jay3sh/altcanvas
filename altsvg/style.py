#
# This file is part of altcanvas.
#
# altcanvas - SVG based GUI framework
# Copyright (C) 2009  Jayesh Salvi <jayeshsalvi@gmail.com>
#
# Distributed under GNU General Public License version 3
#

def load_style(style_str):
    ''' Parse and load style from style string '''
    style = {}
    for style_attr in style_str.strip().split(';'):
        name, value = style_attr.split(':')
        style[name] = value
    return style

def apply_style(ctx, style):
    ''' Modify given contex according to the style '''
    if style.has_key('stroke-width'):
        ctx.set_line_width(float(style['stroke-width']))
    if style.has_key('stroke-miterlimit'):
        ctx.set_miter_limit(float(style['stroke-miterlimit']))


