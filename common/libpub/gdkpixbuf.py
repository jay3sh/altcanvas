#!/usr/bin/env python

# A simple class over GdkPixbuf
# Copyright (C) 2008 Andrea Marchesini
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
import random
import gtk.gdk
import tempfile

class GdkPixbuf:
	def present(self):
		return True
	
	def img2thumb(self,orig_filepath,geometry="150x150"):
		randomstr = str(random.randint(1,999999))
		thumb_filepath = self.temp_dir+os.sep+"publishr-thumb-"+ \
				randomstr+"."+orig_filepath.rpartition(os.sep)[2]
					
		if self.convert(orig_filepath, thumb_filepath, geometry):
			return thumb_filepath
			
		
	def svg2jpeg(self,svg_filepath,jpeg_filepath=None):
		if jpeg_filepath == None:
			randomstr = str(random.randint(1,999999))
			jpeg_filepath = tempfile.gettempdir()+os.sep+"publishr-"+randomstr+".jpg"

		if self.convert(svg_filepath, jpeg_filepath):
			return jpeg_filepath

	def convert(self,source_filepath,target_filepath,geometry=None):
        	pixbuf = gtk.gdk.pixbuf_new_from_file(source_filepath)

		if geometry:
			pixbuf.scale_simple(geometry[0], geometry[1],gtk.gdk.INTERP_NEAREST);

	        pixbuf.save(target_filepath, "jpeg", {"quality" : "100" })

        	return True
				
	def getImageGeometry(self,imagename):
        	pixbuf = gtk.gdk.pixbuf_new_from_file(imagename)
		geometry = (pixbuf.get_width(), pixbuf.get_height())
		return geometry
		
		
if __name__ == "__main__":
	gp = GdkPixbuf()
	print gp.present()
	thumbname = gp.svg2jpeg(sys.argv[1])
	print thumbname
	print gp.getImageGeometry(thumbname)


