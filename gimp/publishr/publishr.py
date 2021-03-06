#!/usr/bin/env python

# Gimp publishr plugin to publish images on web
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

from gimpfu import *

from libpub.utils.crash import handle_crash


def publishr_func(image,drawable):
    try:
        import libpub
        filename = None
        if image != None:
            # Check if file is dirty
            if pdb.gimp_image_is_dirty(image):
                libpub.alert("Please save the image before publishing.")
                return

            filename = pdb.gimp_image_get_filename(image)
        
            if(not (filename.lower().endswith('jpg') or 
                filename.lower().endswith('jpeg') or 
                filename.lower().endswith('gif'))):
             libpub.alert("You have to save the file in jpeg or gif format before publishing") 
             return
    
        if filename:
            libpub.start(hostapp='Gimp',fnames=(filename,))
        else:
            libpub.start(hostapp='Gimp')
        gtk.main()
    except ImportError, impe:
        libpub.alert_markup("Your system seems to be missing following modules."
                     +" Please install them before proceeding further."
                     +"\n\n<b>"+str(impe)+"</b>")
                     
        return
    except:
        handle_crash()    
        return
        
        
try:
    '''    
    if __name__ == '__main__':
        publishr_func(None,None)
    ''' 
    
    register(
        "python_fu_publish",
        "Image publishing plugin",
        "Image publishing plugin",
        "Jayesh Salvi",
        "Jayesh Salvi",
        "2007",
        "<Image>/File/_Publish on Web",
        "RGB*, GRAY*, INDEXED*",
        [],
        [],
        publishr_func)

    main()

except:
    handle_crash()
