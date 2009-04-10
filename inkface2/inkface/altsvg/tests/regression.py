#!/usr/bin/python

import sys
import md5
import pygame
import cairo
import numpy
from copy import copy
import os

import inkface
from inkface.altsvg import VectorDoc

def usage():
    print 'regression.py [options]'
    print 'Options:'
    print '    genpng - generate PNG files from SVG test files'
    print '    cmppng - load PNG files and compare their cairo buffer'
    print '             with the one freshly created from SVG test files'


class SlideShow:
    def rgb_voodo(self,surface):
        buf = surface.get_data()
        a = numpy.frombuffer(buf,numpy.uint8)
        a.shape = (surface.get_width(),surface.get_height(),4)
        tmp = copy(a[:,:,0])
        a[:,:,0] = a[:,:,2]
        a[:,:,2] = tmp
        return a
 
    def load_fresh_image(self,svgname):
        self.vectorDoc = VectorDoc(svgname)
        #self.iw,self.ih = map(lambda x: int(x), self.vectorDoc.get_doc_props())
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
            int(self.vectorDoc.width),int(self.vectorDoc.height))
        ctx = cairo.Context(surface)
        self.vectorDoc.render_full(ctx)

        ctx.move_to(5,10)
        ctx.show_text(svgname+" [FRESH]")
        return surface
 
    def load_saved_image(self,pngname):
        surface = cairo.ImageSurface.create_from_png(pngname)
        ctx = cairo.Context(surface)
        ctx.move_to(5,10)
        ctx.show_text(pngname+" [SAVED]")
        return surface
        
    def main(self,svgfiles):
        self.svgfiles = svgfiles
        svgname = svgfiles[0]
        pygame.init()
        self.w, self.h = (840,740)
        self.window = pygame.display.set_mode(
                        (self.w,self.h),pygame.RESIZABLE )
        self.screen = pygame.display.get_surface()

        self.counter = 0

        while True: 
            self.input(pygame.event.wait())

    def refresh_slide(self, surface):
        buf = self.rgb_voodo(surface)

        image = pygame.image.frombuffer(buf.tostring(),
                    (surface.get_width(),surface.get_height()),"RGBA")

        self.screen.blit(image, (20,20))
        pygame.display.flip() 

       
    def input(self,event):
        if event.type == pygame.QUIT:
            sys.exit(0) 
        elif event.type == pygame.KEYDOWN:
            index = self.counter/2
            if(index < len(self.svgfiles)):
                if(self.counter%2 == 0):
                    surface = self.load_saved_image(
                            self.svgfiles[index].replace('svg','png'))
                else:
                    surface = self.load_fresh_image(self.svgfiles[index])
                    
                self.refresh_slide(surface)
                self.counter += 1
            else:
                sys.exit(0)


def main():
    op = sys.argv[1]

    SVG_FILES = map(lambda x: 'data/shape-%d.svg'%x, range(19))
    SVG_FILES += (map(lambda x: 'data/composite-%d.svg'%x, range(2)))

    if op == 'genpng':
        # Generate PNG files from SVG test files
        for file in SVG_FILES:
            if os.path.exists(file.replace('svg','png')):
                print 'Skipping '+file
                continue

            vdoc = VectorDoc(file)
            #w,h = map(lambda x: int(x), vdoc.get_doc_props())
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                int(vdoc.width),
                int(vdoc.height))
            ctx = cairo.Context(surface)
            vdoc.render_full(ctx)

            print 'Saving PNG image for '+file
            surface.write_to_png(file.replace('svg','png'))

    elif op == 'cmppng':

        for file in SVG_FILES:
            sys.stdout.write('Checking '+file+' ')
            vdoc = VectorDoc(file)
            #w,h = map(lambda x: int(x), vdoc.get_doc_props())
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                int(vdoc.width),
                int(vdoc.height))
            ctx = cairo.Context(surface)
            vdoc.render_full(ctx)
            
            fresh_buf = surface.get_data()
            fresh_md5 = md5.new()
            fresh_md5.update(fresh_buf)

            png_surface = cairo.ImageSurface.create_from_png(
                            file.replace('svg','png'))
            saved_buf = png_surface.get_data()
            saved_md5 = md5.new()
            saved_md5.update(saved_buf)

            if fresh_md5.digest() == saved_md5.digest():
                sys.stdout.write('... passed\n')
            else:
                sys.stdout.write('... failed\n')
    elif op == 'viscmp':
        SlideShow().main(SVG_FILES)    
    else:
        usage()
        sys.exit(0)

if __name__ == '__main__':
    main()
