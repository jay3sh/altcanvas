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
	
	def img2thumb_pixbuf(self,orig_filepath,geometry=(150,150)):
		return self.scale(orig_filepath, geometry)
			
	def img2thumb(self,orig_filepath,geometry=(150,150)):
		randomstr = str(random.randint(1,999999))
		thumb_filepath = tempfile.gettempdir()+os.sep+"publishr-thumb-"+ \
				randomstr+"."+orig_filepath.rpartition(os.sep)[2]
		pb = self.img2thumb_pixbuf(orig_filepath, geometry)
		pb.save(thumb_filepath,"jpeg",{"quality":"100"})
		return thumb_filepath
		
	def svg2jpeg(self,svg_filepath):
		randomstr = str(random.randint(1,999999))
		jpeg_filepath = tempfile.gettempdir()+os.sep+"publishr-"+randomstr+".jpg"

		pixbuf = gtk.gdk.pixbuf_new_from_file(svg_filepath)
		pixbuf.save(jpeg_filepath,"jpeg",{"quality":"100"})
		return jpeg_filepath

	def scale(self,source_filepath,geometry=None):
		pixbuf = gtk.gdk.pixbuf_new_from_file(source_filepath)

		if geometry:
			width = geometry[0]
			height = geometry[1]
			target_pixbuf = pixbuf.scale_simple(width,height,gtk.gdk.INTERP_NEAREST);
			return target_pixbuf
		else:
			return None
            
		
		
if __name__ == "__main__":
	gp = GdkPixbuf()
	print gp.present()
	thumbname = gp.svg2jpeg(sys.argv[1])
	print thumbname


