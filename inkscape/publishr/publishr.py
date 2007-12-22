#!/usr/bin/env python 
"""
publishr.py
An extention 

"""

import os
import sys

import gtk

import libpub
import libpub.gui
import libpub.imagic

try:
	im = libpub.imagic.ImageMagick()
	if not im.present():
		libpub.alert("You need to install ImageMagick for this plugin to work.")
	
	svgfilename = sys.argv[1]
	libpub.filename = im.svg2jpeg(svgfilename)
	
	libpub.config = libpub.Config()
	libpub.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	libpub.window.connect("delete_event",libpub.delete_event)
	libpub.window.connect("destroy",libpub.destroy)
        
	gui = libpub.gui.UploadGUI()
    
	libpub.window.show()
	gtk.main()
	
	os.remove(libpub.filename)
except:
    libpub.handle_crash()    
	



