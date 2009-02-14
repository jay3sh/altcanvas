#!/usr/bin/python

import sys
import md5
import cairo
import altsvg

def usage():
    print 'regression.py [options]'
    print 'Options:'
    print '    genpng - generate PNG files from SVG test files'
    print '    cmppng - load PNG files and compare their cairo buffer'
    print '             with the one freshly created from SVG test files'


def main():
    op = sys.argv[1]

    SVG_FILES = map(lambda x: 'data/shape-%d.svg'%x, range(8))
    SVG_FILES += (map(lambda x: 'data/composite-%d.svg'%x, range(1)))

    if op == 'genpng':
        # Generate PNG files from SVG test files
        for file in SVG_FILES:
            vdoc = altsvg.VectorDoc(file)
            w,h = map(lambda x: int(x), vdoc.get_doc_props())
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
            ctx = cairo.Context(surface)
            vdoc.render_full(ctx)

            surface.write_to_png(file.replace('svg','png'))

    elif op == 'cmppng':

        for file in SVG_FILES:
            sys.stdout.write('Checking '+file+' ')
            vdoc = altsvg.VectorDoc(file)
            w,h = map(lambda x: int(x), vdoc.get_doc_props())
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,w,h)
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
                sys.stdout.write('... pass\n')
            else:
                sys.stdout.write('... failed\n')

    else:
        usage()
        sys.exit(0)

if __name__ == '__main__':
    main()
