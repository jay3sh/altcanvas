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
from libpub.utils.crash import handle_crash

try:
	import libpub
	import libpub.gui
	import libpub.gdkpixbuf

	gp = libpub.gdkpixbuf.GdkPixbuf()
	
	svgfilename = sys.argv[1]
	jpegfilename = gp.svg2jpeg(svgfilename)

	
	if jpegfilename:
		libpub.start(hostapp='Inkscape',fname=jpegfilename)		
	else:
		libpub.alert("JPEG file not created")
	
	gtk.main()
	
	if svgfilename:
		os.remove(svgfilename)

except ImportError, impe:
    libpub.alert_markup("Your system seems to be missing following modules."
                 +" Please install them before proceeding further."
                 +"\n\n<b>"+str(impe)+"</b>")
                     
except:
    handle_crash()
        
	



