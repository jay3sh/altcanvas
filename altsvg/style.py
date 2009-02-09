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

class Style:
    def __init__(self,style_str):
        ''' Parse and load style from style string '''
        self.__style__ = {}
        for style_attr in style_str.strip().split(';'):
            name, value = style_attr.split(':')
            self.__style__[name] = value

    def __getattr__(self,key):
        ''' Override the getter to provide easy access to style attributes '''
        if self.__dict__.has_key(key): return self.__dict__[key]

        modkey = key.replace('_','-')
        if self.__style__.has_key(modkey): return self.__style__[modkey]

        raise AttributeError('Unknown attr '+key)

    def __html2rgb(self,html_color):
        ''' Converts HTML color code to normalized RGB values '''
        r = int(html_color[1:3], 16)
        g = int(html_color[3:5], 16)
        b = int(html_color[5:7], 16)
        return (r/256., g/256., b/256.)


    def apply_stroke(self,ctx):
        ''' 
        Modify given context according to the style
            @return True if stroke is specified
                    False if stroke is not specified 
        '''
        r = g = b = 0.0
        a = 1.0
        if self.__style__.has_key('stroke'):
            if self.__style__['stroke'] == 'none':
                return False
            r, g, b = self.__html2rgb(self.__style__['stroke'])
        if self.__style__.has_key('stroke-opacity'):
            a = float(self.__style__['stroke-opacity'])
    
        ctx.set_source_rgba(r, g, b, a)
    
        if self.__style__.has_key('stroke-width'):
            ctx.set_line_width(float(self.__style__['stroke-width']))
        if self.__style__.has_key('stroke-miterlimit'):
            ctx.set_miter_limit(float(self.__style__['stroke-miterlimit']))
            
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


    def has(self,prop):
        return self.__style__.has_key(prop) and \
            self.__style__[prop] != self.__noval[prop]


