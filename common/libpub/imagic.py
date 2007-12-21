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

class ImageMagick:
	imagicdir = None
	convert_bin = None
	temp_dir = None
	def __init__(self):
		pass

	def present(self):
		if sys.platform.find('win32') >= 0:
			# WINDOWS
			programdirs = os.listdir("C:\\Program Files\\")
			for programdir in programdirs:
				if programdir.find('ImageMagick') >= 0:
					self.imagicdir = "C:\\Program Files\\"+programdir
					break
			if self.imagicdir:
				self.convert_bin = '"'+self.imagicdir+"\\convert"+'"'
			else:
				return False
			
			self.temp_dir = os.getenv('USERPROFILE')+'\\'
		else:
			# LINUX
			self.convert_bin = '/usr/bin/convert'
			self.identify_bin = '/usr/bin/identify'
			self.temp_dir = '/tmp'
			
		# Generic code
		(sin,souterr) = os.popen4('%s --version'%self.convert_bin)
		for line in souterr:
			if line.find('ImageMagick') >= 0:
				return True
		return False
	
	def makeThumbnail(self,filename,geometry="150x150"):
		try:
			randomstr = str(random.randint(1,999999))
			thumbname = self.temp_dir+os.sep+"publishr-thumb-"+randomstr+"-"+filename.rpartition(os.sep)[2]
			geometry = "-geometry %s"%geometry
			(sin,souterr) = os.popen4('%s %s %s %s'%
								  (self.convert_bin,filename,geometry,thumbname))
			for line in souterr:
				if line != None:
					print "Error creating thumbnail: %s"%line
					return None
			return thumbname
		except Exception, e:
			return None
		
	def deleteThumbnail(self,thumbname):
		try:
			os.remove(thumbname)
		except Exception, e:
			return None
			
		
	def getThumbnailGeometry(self,thumbname):
		try:
			(sin,souterr) = os.popen4('%s %s'%(self.identify_bin,thumbname))
			for line in souterr:
				propstring = line
			geometry = propstring.split()[2]
			return geometry
		except Exception, e:
			return None
		
if __name__ == "__main__":
	im = ImageMagick()
	print im.present()
	thumbname = im.makeThumbnail("/downloads/altimages/rainbow.jpg")
	print thumbname
	print im.getThumbnailGeometry(thumbname)


