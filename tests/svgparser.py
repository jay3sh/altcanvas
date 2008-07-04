#!/usr/bin/python2.5

'''
import utils

fd = open('/photos/altimages/cartoons/test2.svg')
svg_content = ''
for line in fd:
    svg_content += line

svgnode = utils.XMLNode().parseXML(svg_content)

print '-----------'

print svgnode.g[0].g[1]['id']

print svgnode.g[0].elementText
'''

import sys

boilerplate = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>'
fd = open('/photos/altimages/cartoons/test1.svg')
svg_content = ''
for line in fd:
    svg_content += line


import xml.dom.minidom

dom = xml.dom.minidom.parseString(svg_content)

class SVGParser:
    def __init__(self,svgdoc):
        self.doc = svgdoc

    def makeSVGBase(self):
        self.svg_base = boilerplate
    
    def createWidget(self,obj):
        if 'class' in obj.attributes.keys():
            print obj.toxml()
    
    def die(self,msg):
        print msg
        sys.exit(1)
    
    def parse(self):
        svg = self.doc.getElementsByTagName('svg')
        if len(svg) > 1: self.die('svg')
    
        defs = self.doc.getElementsByTagName('defs')
        if len(defs) > 1: self.die('defs')
    
        sodipodi = self.doc.getElementsByTagName('sodipodi:namedview')
        if len(sodipodi) > 1: self.die('sodipodi')
    
        metadata = self.doc.getElementsByTagName('metadata')
        if len(metadata) > 1: self.die('metadata')
    
        for obj in ['g','path','rect']:
            for i in self.doc.getElementsByTagName(obj):
                self.createWidget(i)

if __name__ == '__main__':
    sp = SVGParser(dom)
    sp.parse()
