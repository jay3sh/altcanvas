#!/usr/bin/env python 

# Publishr to publish images on web
# Copyright (C) 2007  Jayesh Salvi 
# http://www.altcanvas.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import sys

import gtk

import libpub
import libpub.gui
import libpub.imagic

try:
	im = libpub.imagic.ImageMagick()
	
	if im.present():
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
	else:
		libpub.alert("You need to install ImageMagick for this plugin to work.")
		
except:
    libpub.handle_crash()    
	



