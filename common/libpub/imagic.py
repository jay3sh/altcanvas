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
import random

import libpub

class ImageMagick:
	imagicdir = None
	convert_bin = None
	temp_dir = None
	
	def __init__(self):
		if sys.platform.find('win32') >= 0:
			# WINDOWS
			programdirs = os.listdir("C:\\Program Files\\")
			for programdir in programdirs:
				if programdir.find('ImageMagick') >= 0:
					self.imagicdir = '"C:\\Program Files\\'+programdir
					break
			if self.imagicdir:
				self.convert_bin = self.imagicdir+'\\convert"'
			else:
				raise Exception('ImageMagick wasn\'t found')
			
			self.temp_dir = os.getenv('USERPROFILE')+'\\'
		else:
			# LINUX
			self.convert_bin = '/usr/bin/convert'
			self.identify_bin = '/usr/bin/identify'
			self.temp_dir = '/tmp'

	def present(self):
			
		# Generic code
		command = '%s --version'%self.convert_bin
		print command
		(sin,sout,serr) = os.popen3(command)
		for line in sout:
			if line.find('ImageMagick') >= 0:
				return True
		return False
	
	def img2thumb(self,orig_filepath,geometry="150x150"):
		randomstr = str(random.randint(1,999999))
		thumb_filepath = self.temp_dir+os.sep+"publishr-thumb-"+\
				randomstr+"."+orig_filepath.rpartition(os.sep)[2]
					
		if self.convert(orig_filepath, thumb_filepath, geometry):
			return thumb_filepath
			
		
	def svg2jpeg(self,svg_filepath,jpeg_filepath=None):
		# If target jpeg filename not given create a random temp name
		if jpeg_filepath == None:
			randomstr = str(random.randint(1,999999))
			jpeg_filepath = self.temp_dir+os.sep+"publishr-"+randomstr+".jpg"
				
		if self.convert(svg_filepath, jpeg_filepath):
			return jpeg_filepath
		
		
	def convert(self,source_filepath,target_filepath,geometry=None):
		if geometry:
			geometry_arg = "-geometry %s"%geometry
		else:
			geometry_arg = " "
				
		command = '%s "%s" %s "%s"'% \
				  (self.convert_bin,source_filepath,geometry_arg,target_filepath)
		
		(sin,sout,serr) = os.popen3(command)
			
		# "convert" won't put anything on stderr if it's successful
		for line in serr:
			if line != None:
				raise Exception("ImageMagick convert failure: %s"%line)
				
		return True
		
		
	def getImageGeometry(self,imagename):
		(sin,sout,serr) = os.popen3('%s %s'%(self.identify_bin,imagename))
		for line in sout:
			propstring = line
		geometry = propstring.split()[2]
		return geometry
		
		
if __name__ == "__main__":
	im = ImageMagick()
	print im.present()
	thumbname = im.makeThumbnail("/downloads/altimages/rainbow.jpg")
	print thumbname
	print im.getThumbnailGeometry(thumbname)


