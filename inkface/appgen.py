#!/usr/bin/python

import sys
import getopt

def generate_project(destdir,name):
    import os
    SEP = os.path.sep

    '''
    if not os.path.exists(destdir):
        path_segments = destdir.split(SEP)
        destdir_parent = SEP.join(path_segments[:-1])
        if not os.path.exists(destdir_parent):
            print "Parent directory does not exist: "+destdir_parent
            sys.exit(1)

        else:
            try:
                os.mkdir(destdir)
            except Exception, e:
                print 'Error creating project dir: '+str(e)
                sys.exit(1)
    '''
    
    os.makedirs(destdir+SEP+name+SEP+'svg')
    os.makedirs(destdir+SEP+name+SEP+'code')

    # write a template .svg file under svg

    # write a template .py file under code

    # write a setup.py

def usage():
    print 'Inkface App generation script:'
    print ' appgen.py [options]'
    print ' '
    print ' -d --dir : destination directory to generate project files'
    print ' -h --help: usage'

def main():
    args = sys.argv[1:]

    try:
        optlist, args = getopt.getopt(args,'hd:n:',['help','dir=','name='])
    except getopt.GetoptError, err:
        print str(err)
        usage()
        sys.exit(0)
    
    for o,a in optlist:
        if o in ('-h','--help'):
            usage()
            break
        elif o in ('-d','--dir'):
            destdir = a
        elif o in ('-n','--name'):
            name = a
            
    if destdir and name:
        generate_project(name=name, destdir=destdir)

if __name__ == '__main__':
    main()
