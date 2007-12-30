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

'''publishr plugin library '''

import os
import sys
import gtk

window = None
conf = None
filename = '/tmp/test123.jpg'
CONFIG_FILE = ''

SERVER = 'http://www.altcanvas.com/xmlrpc/'
VERSION = '0.3.2'
HOSTAPP = '_'
    
def start(hostapp='_'):
    global conf,window
    import utils.config
    import control
    HOSTAPP = hostapp
    conf = utils.config.Config()
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("delete_event",delete_event)
    window.connect("destroy",destroy)
        
    _control = control.Control(window)
    _control.entry()
        
    window.show()
    
        
LicenseList = [
    (0,"All rights reserved",
         None),
    (4,"Attribution License",
         "http://creativecommons.org/licenses/by/2.0/"),
    (6,"Attribution-NoDerivs License",
         "http://creativecommons.org/licenses/by-nd/2.0/"),
    (3,"Attribution-NonCommercial-NoDerivs License",
         "http://creativecommons.org/licenses/by-nc-nd/2.0/"),
    (2,"Attribution-NonCommercial License",
         "http://creativecommons.org/licenses/by-nc/2.0/"),
    (1,"Attribution-NonCommercial-ShareAlike License",
         "http://creativecommons.org/licenses/by-nc-sa/2.0/"),
    (5,"Attribution-ShareAlike License",
         "http://creativecommons.org/licenses/by-sa/2.0/")
]
        
def alert(msg,type=gtk.MESSAGE_ERROR):
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()

def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()

def signout(widget=None,data=None):
    conf.set('FLICKR_TOKEN',None)
    # Quit the GUI
    destroy()
    
    
    
