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

        

import gtk

import libpub

########################################
# Picasaweb API
########################################
import libpub.atom as atom
import libpub.gdata.service
import libpub.gdata as gdata
import libpub.gdata.base
import libpub.gdata.photos.service

class PicasawebObject:
    picweb=None
    def __init__(self):
        self.picweb = libpub.gdata.photos.service.PhotosService()
        self.picweb.source = 'Publishr'
    
    def login(self,username,password):
        self.picweb.ClientLogin(username,password)
    
class PicasawebRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        self.parentgui = parent
        self.picwebObject = self.parentgui.picwebObject
        # Picasaweb Login widgets
        self.loginTitle = gtk.Label('Login to your Picasaweb (Google) account')
        self.usernameTitle = gtk.Label('Username')
        self.usernameEntry = gtk.Entry()
        self.usernameEntry.set_width_chars(15)
        self.passwordTitle = gtk.Label('Password')
        self.passwordEntry = gtk.Entry()
        self.passwordEntry.set_visibility(False)
        self.passwordEntry.set_width_chars(15)
        self.passwordExplainLabel = gtk.Label(
            "Your password is passed to Google's GDATA library which does "+
            "the authentication over SSL connection. It is NOT sent anywhere "+
            "else on network or stored on disk in plaintext")
        self.passwordExplainLabel.set_width_chars(52)
        self.passwordExplainLabel.set_line_wrap(True)
        self.loginButton = gtk.Button('Login')
        self.loginButton.connect("clicked",self.login_handler)
        self.cancelButton = gtk.Button('Cancel')
        self.cancelButton.connect("clicked",libpub.destroy)
        
        self.remember_check = gtk.CheckButton('Remember username')
        
        self.usernameBox = gtk.HBox()
        self.usernameBox.pack_start(self.usernameTitle,expand=False)
        self.usernameBox.pack_start(self.usernameEntry,expand=False)
        self.usernameBox.set_homogeneous(True)
        self.passwordBox = gtk.HBox()
        self.passwordBox.pack_start(self.passwordTitle,expand=False)
        self.passwordBox.pack_start(self.passwordEntry,expand=False)
        self.passwordBox.set_homogeneous(True)
        self.rememberBox = gtk.HBox()
        self.rememberBox.pack_start(gtk.Label('   '))
        self.rememberBox.pack_start(self.remember_check,expand=True)
        self.passwordBox.set_homogeneous(True)
        self.buttonBox = gtk.HBox()
        self.buttonBox.pack_start(self.loginButton)
        self.buttonBox.pack_start(self.cancelButton)
            
        self.set_spacing(15)
        self.pack_start(self.loginTitle)
        self.pack_start(self.usernameBox)
        self.pack_start(self.passwordBox)
        self.pack_start(self.rememberBox)
        self.pack_start(self.passwordExplainLabel)
        self.pack_start(self.buttonBox)
        self.set_border_width(30)
        
        # Recall last settings, if available
        last_username = libpub.config.get('PICASA_LAST_USERNAME')
        if last_username:
            # Load the remembered username
            self.usernameEntry.set_text(last_username)
            # Now the focus must go to password to start with
            self.passwordBox.grab_focus()
            self.passwordEntry.grab_focus()
            # Safe to assume user wants to remember the username again
            self.remember_check.set_active(True)
        else:
            # Let us not assume user wants us to remember username
            self.remember_check.set_active(False)
            # No username available, so focus should go to username entry
            self.usernameBox.grab_focus()
            self.usernameEntry.grab_focus()
        
        self.show_all()
        
    def login_handler(self,widget,data=None):
        username = self.usernameEntry.get_text()
        password = self.passwordEntry.get_text()
        try:
            self.parentgui.picwebObject.login(username,password)
            self.parentgui.upload_dialog()
            if self.remember_check.get_active():
                libpub.config.set('PICASA_LAST_USERNAME',username)
            else:
                libpub.config.set('PICASA_LAST_USERNAME',None)
        except Exception, e:
            libpub.alert('Login error: %s'%e)
