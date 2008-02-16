
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
import gtk
import pango

import libpub

from libpub.picasa import PicasawebObject
from libpub.gdata.photos.service import PicasaException

def empty_window():
    for box in libpub.window.get_children():
        libpub.window.remove(box)
    libpub.window.resize(10,10)
        
class Entry(gtk.VBox):
    ''' Main GUI container '''
    def __init__(self,flickr_handler=None,picasa_handler=None):
        gtk.VBox.__init__(self)
        self.type = None
        self.webservice = None
        
        # Service choice widgets
        self.flickrButton = gtk.Button('_Flickr')
        self.picwebButton = gtk.Button('_Picasaweb')
        
        self.flickrButton.connect("clicked",flickr_handler,self)
        self.picwebButton.connect("clicked",picasa_handler,self)
        
        self.introLabel = gtk.Label()
        self.introLabel.set_markup('\
<span font_family="sans" size="large" weight="heavy" >\
<span foreground="#000015">P</span>\
<span foreground="#00002A">u</span>\
<span foreground="#00003F">b</span>\
<span foreground="#000054">l</span>\
<span foreground="#000069">i</span>\
<span foreground="#00007E">s</span>\
<span foreground="#000093">h</span>\
<span foreground="#000000"> </span>\
<span foreground="#0000A8">o</span>\
<span foreground="#0000BD">n</span>\
<span foreground="#000000"> </span>\
<span foreground="#0000D2">w</span>\
<span foreground="#0000E7">e</span>\
<span foreground="#0000FC">b</span>\
<span foreground="#0000FF">!</span>\
</span>')
        
        ##
        #    Save service (Flickr/Picasa) choice
        ##
        def service_memory_toggled(togglebutton,param=None):
            if self.serviceMemory.get_active():
                self.remember_service = True
            else:
                self.remember_service = False
        
        self.remember_service = False
        self.serviceMemory = gtk.CheckButton(label='Remember choice')
        self.serviceMemory.connect('toggled',service_memory_toggled)
        

        # Pack all widgets
        self.pack_start(self.introLabel,expand=False)
        self.pack_start(self.flickrButton,expand=False)
        self.pack_start(self.picwebButton,expand=False)
        self.pack_start(self.serviceMemory,expand=False)
        self.set_spacing(10)
        
        self.set_border_width(15)
        self.show_all()
        
class UploadDlg(gtk.VBox):
    '''
        Upload dialog 
    '''
    def __init__(self,parent):
        '''
        @param service_choice: photo hosting service type {FLICKR,PICASAWEB}
        @param parent: handle to the parent control object
        '''
        gtk.VBox.__init__(self)
        if libpub.SERVICE_CHOICE == 'FLICKR':
            self.flickr = parent.flickr
        else:
            self.picasa = parent.picasa
        
        #
        #    Photosets/Albums
        #
        albumLabel = None
        albums = None
        i = 0
        select_album = 0
        self.albumCombo = gtk.combo_box_entry_new_text()
        if libpub.SERVICE_CHOICE == 'FLICKR':
            albumLabel = gtk.Label('Photosets')
            albums = self.flickr.get_photosets()
            last_album = libpub.conf.get('FLICKR_LAST_PHOTOSET')
            for album in albums:
                self.albumCombo.append_text(album['title'])
                if album['title'] == last_album:
                    select_album = i
                i += 1
            self.albumCombo.set_active(select_album)
            
            
        elif libpub.SERVICE_CHOICE == 'PICASAWEB':
            albumLabel = gtk.Label('Albums')
            pws = self.picasa.picweb
            albums = pws.GetUserFeed().entry
            last_album = libpub.conf.get('PICASA_LAST_ALBUM')
            for album in albums:
                self.albumCombo.append_text(album.title.text)
                if album.name.text == last_album:
                    select_album = i
                i += 1
            self.albumCombo.set_active(select_album)
            
        ##
        #    Title
        ##
        titleLabel = gtk.Label('Title')
        self.titleEntry = gtk.Entry()
        
        ##
        #    Description/Summary
        ##
        descLabel = gtk.Label('Description')
        dsw = gtk.ScrolledWindow()
        dsw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.descView = gtk.TextView()
        self.descView.set_wrap_mode(gtk.WRAP_WORD)
        self.descView.set_accepts_tab(False)
        dsw.add(self.descView)

        ##
        #    Tags
        ##
        tagLabel = gtk.Label('Tags')
        self.tagEntry = gtk.Entry()
        
        ##
        #    Licenses
        ##
        licenseLabel = gtk.Label('License')
        self.licenseCombo = gtk.combo_box_entry_new_text()
        for lic in libpub.LicenseList:
            self.licenseCombo.append_text(lic[1])
        last_license = libpub.conf.get('LAST_LICENSE_USED')
        
        if last_license:
            last_license_index = int(last_license) 
            if last_license_index >= 0 and  last_license_index < len(libpub.LicenseList)-1:
                self.licenseCombo.set_active(int(last_license))
            else:
                self.licenseCombo.set_active(0)
        else:
            self.licenseCombo.set_active(0)
        
        ##
        #    Public/Private
        ##
        def privacy_toggled(togglebutton,param=None):
            if self.privacyCheck.get_active():
                self.is_public = '1'
            else:
                self.is_public = '0'
        
        self.privacyCheck = gtk.CheckButton(label='Public')
        self.privacyCheck.connect('toggled',privacy_toggled)
        
        # Recall what was the setting last time
        self.is_public =  libpub.conf.get('LAST_PRIVACY_CHOICE') or '1'
        self.privacyCheck.set_active(self.is_public == '1')

        ##
        #    OK
        ##
        okButton = gtk.Button('Upload')
        okButton.connect("clicked",parent.upload)
        
        ##
        #    Cancel
        ##
        cancelButton = gtk.Button('Quit')
        cancelButton.connect("clicked",libpub.destroy)
        
        ##
        #    Signout
        ##
        signoutButton = gtk.Button('Sign out')
        signoutButton.connect("clicked",libpub.signout)
        
        ##
        #    Home
        ##
        homepb = gtk.gdk.pixbuf_new_from_xpm_data(libpub.home_xpm)
        homeimg = gtk.Image()
        homeimg.set_property('pixbuf',homepb)
        homeButton = gtk.Button()
        homeButton.set_image(homeimg)
        homeButton.connect("clicked",parent.display_home)
        
        
        #####
        # packing of widgets
        #####
        albumBox = gtk.HBox()
        albumBox.pack_start(albumLabel)
        albumBox.pack_start(self.albumCombo)
        albumBox.set_border_width(4)
        
        titleBox = gtk.HBox()
        titleBox.pack_start(titleLabel)
        titleBox.pack_start(self.titleEntry)
        titleBox.set_border_width(4)

        descBox = gtk.VBox()
        descLabelBox = gtk.HBox()
        descLabelBox.pack_start(descLabel,expand=False,fill=False)
        descBox.pack_start(descLabelBox)
        descBox.pack_start(dsw)
        descBox.set_border_width(4)

        tagBox = gtk.HBox()
        tagBox.pack_start(tagLabel)
        tagBox.pack_start(self.tagEntry)
        tagBox.pack_start(self.privacyCheck)
        tagBox.set_border_width(4)

        licenseBox = gtk.HBox()
        licenseBox.pack_start(licenseLabel)
        licenseBox.pack_start(self.licenseCombo)

        inputBox = gtk.VBox()
        inputBox.pack_start(titleBox)
        inputBox.pack_start(descBox)
        inputBox.pack_start(albumBox)
        inputBox.pack_start(tagBox)
        inputBox.pack_start(licenseBox)
        inputBox.set_border_width(4)

        buttonBox = gtk.HBox()
        buttonBox.pack_start(okButton)
        buttonBox.pack_start(cancelButton)
        buttonBox.pack_start(signoutButton)
        buttonBox.pack_start(homeButton)
        buttonBox.set_border_width(4)

        self.pack_start(inputBox)
        self.pack_start(buttonBox)
        self.set_border_width(6)
        
        self.show_all()
        
        if libpub.SERVICE_CHOICE == 'PICASAWEB':
            self.privacyCheck.hide()
            
            # Set the title to be the filename
            if len(libpub.filename_list) == 1:
                path_segments = libpub.filename_list[0].split(os.sep)
                self.title = path_segments[len(path_segments)-1]
                self.titleEntry.set_text(self.title)
            
            # Add a blank-license option to license choices. This will result
            # into appending nothing to the summary field about license info
            self.licenseCombo.append_text('Don\'t mention licensing info')
            model = self.licenseCombo.get_model()
            # Try to recall previous license choice
            last_license = libpub.conf.get('LAST_LICENSE_USED')
            if last_license:
                self.licenseCombo.set_active(int(last_license))
            else:
                # choose blank-license option
                self.licenseCombo.set_active(len(model)-1)
                
        
class FlickrRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        self.flickr = parent.flickr
        
        ##
        #    Explanation label for password non-storage policy
        ##
        self.explainLabel = gtk.Label(
        'Please copy the following link and open it using your web browser.'+
        'Flickr will ask you to authorize AltCanvas to upload photos to your account.'+
        'You will have to click on "OK, I\'ll allow it" to be able to use this plugin.')
        self.explainLabel.set_width_chars(45)
        self.explainLabel.set_line_wrap(True)
        
        ##
        #    Authentication URL box
        ##
        self.urlText = gtk.Entry()
        self.urlText.set_width_chars(45)
        
        authurl = parent.flickr.get_authurl()
        self.urlText.set_text(authurl)
        self.urlText.select_region(0,-1)
        self.urlText.set_editable(False)
        
        ##
        #    A button to open the link in browser
        ##
        self.browserButton = gtk.Button('Open above link in browser')
        self.browserButton.set_border_width(5)
        if libpub.HOSTAPP == 'Maemo':
            authurl = authurl.replace('www','m')
        self.browserButton.connect("clicked",open_browser,authurl)
        
        ##
        #    Done granting permissions, proceed to authentication
        ##
        self.doneButton = gtk.Button('Press when you have granted authorization to AltCanvas!')
        self.doneButton.set_border_width(5)
        self.doneButton.connect("clicked",parent.flickr_login_handler)
        
        homepb = gtk.gdk.pixbuf_new_from_xpm_data(libpub.home_xpm)
        homeimg = gtk.Image()
        homeimg.set_property('pixbuf',homepb)
        self.homeButton = gtk.Button()
        self.homeButton.set_image(homeimg)
        self.homeButton.connect("clicked",parent.display_home)
        
        self.set_spacing(15)
        self.pack_start(self.explainLabel)
        self.pack_start(self.urlText)
        self.pack_start(self.browserButton)
        self.pack_start(self.doneButton)
        self.pack_start(self.homeButton,expand=False)
        self.set_border_width(30)
        self.show_all()
        
        
class PicasawebRegisterBox(gtk.VBox):
    def __init__(self,parent):
        gtk.VBox.__init__(self)
        # Picasaweb Login widgets
        self.loginTitle = gtk.Label('Login to your Picasaweb (Google) account')
        self.usernameTitle = gtk.Label('Username')
        self.usernameEntry = gtk.Entry()
        self.usernameEntry.set_width_chars(15)
        self.passwordTitle = gtk.Label('Password')
        self.passwordEntry = gtk.Entry()
        self.passwordEntry.set_visibility(False)
        self.passwordEntry.set_width_chars(15)
        self.loginButton = gtk.Button('Login')
        self.loginButton.connect("clicked",parent.picasa_login_handler)
        self.cancelButton = gtk.Button('Cancel')
        self.cancelButton.connect("clicked",libpub.destroy)
        
        homepb = gtk.gdk.pixbuf_new_from_xpm_data(libpub.home_xpm)
        homeimg = gtk.Image()
        homeimg.set_property('pixbuf',homepb)
        self.homeButton = gtk.Button()
        self.homeButton.set_image(homeimg)
        self.homeButton.connect("clicked",parent.display_home)
        
        self.remember_user_check = gtk.CheckButton('Remember username')
        
        self.remember_pass_check = gtk.CheckButton('Remember password')
        self.remember_pass_help = gtk.Button('?')
        self.remember_pass_help.connect('clicked',
                lambda dlg: libpub.alert(
                    'The password will not be stored in plain text, '
                    'however it is possible for a knowledgeable person to decrypt it. '
                    'While logging in it is passed to Google\'s GDATA library which does'
                    ' the authentication over SSL connection.',
                                         gtk.MESSAGE_INFO))
        
        self.usernameBox = gtk.HBox()
        self.usernameBox.pack_start(self.usernameTitle,expand=False)
        self.usernameBox.pack_start(self.usernameEntry,expand=False)
        self.usernameBox.set_homogeneous(True)
        self.passwordBox = gtk.HBox()
        self.passwordBox.pack_start(self.passwordTitle,expand=False)
        self.passwordBox.pack_start(self.passwordEntry,expand=False)
        self.passwordBox.set_homogeneous(True)
        
        self.rememberUserBox = gtk.HBox()
        self.rememberUserBox.pack_start(gtk.Label('   '))
        self.rememberUserBox.pack_start(self.remember_user_check,expand=True)
        self.rememberPasswordBox = gtk.HBox()
        self.rememberPasswordBox.pack_start(gtk.Label('    '))
        self.rememberPasswordBox.pack_start(self.remember_pass_check,expand=True)
        self.rememberPasswordBox.pack_start(self.remember_pass_help,expand=False)
        self.rememberBox = gtk.VBox()
        self.rememberBox.pack_start(self.rememberUserBox)
        self.rememberBox.pack_start(self.rememberPasswordBox)
        
        self.passwordBox.set_homogeneous(True)
        self.buttonBox = gtk.HBox()
        self.buttonBox.pack_start(self.loginButton)
        self.buttonBox.pack_start(self.cancelButton)
        self.buttonBox.pack_start(self.homeButton,expand=False)
            
        self.set_spacing(15)
        self.pack_start(self.loginTitle)
        self.pack_start(self.usernameBox)
        self.pack_start(self.passwordBox)
        self.pack_start(self.rememberBox)
        self.pack_start(self.buttonBox)
        self.set_border_width(30)
        
        # Recall last settings, if available
        last_username = libpub.conf.get('PICASA_LAST_USERNAME')
        if last_username:
            # Load the remembered username
            self.usernameEntry.set_text(last_username)
            # Now the focus must go to password to start with
            self.passwordBox.grab_focus()
            self.passwordEntry.grab_focus()
            # Safe to assume user wants to remember the username again
            self.remember_user_check.set_active(True)
        else:
            # Let us not assume user wants us to remember username
            self.remember_user_check.set_active(False)
            # No username available, so focus should go to username entry
            self.usernameBox.grab_focus()
            self.usernameEntry.grab_focus()
            
        last_password_cipher = libpub.conf.get('PICASA_LAST_PASSWORD')
        if last_password_cipher:
            last_password = libpub.utils.decrypt(last_password_cipher)
            self.passwordEntry.set_text(last_password)
            self.loginButton.grab_focus()
            self.remember_pass_check.set_active(True)
        else:
            self.remember_pass_check.set_active(False)
        
        self.show_all()
        
        
class SuccessDialog(gtk.Dialog):
    def __init__(self,url):
        gtk.Dialog.__init__(self,'Upload successful')
        urlLabel = gtk.Label()
        urlLabel.set_markup('URL to uploaded image <span foreground="blue">%s</span>'%url)
        
        #firefox_pb = gtk.gdk.pixbuf_new_from_xpm_data(libpub.firefox_xpm)
        if libpub.HOSTAPP == 'Maemo':
            browserButton = gtk.Button('Open in Browser')
        else:
            browserButton = gtk.Button('Open in Firefox')
            
        #browserButton.set_image(gtk.image_new_from_pixbuf(firefox_pb))
        browserButton.connect("clicked",self.open_browser_and_quit,url)
        
        doneButton = gtk.Button('Done')
        doneButton.connect("clicked",self.respond_done)
        
        buttonBox = gtk.HBox()
        buttonBox.pack_start(browserButton)
        buttonBox.pack_start(doneButton)
        
        self.vbox.pack_start(urlLabel)
        self.vbox.pack_start(buttonBox)
        self.vbox.set_spacing(10)
        self.set_border_width(25)
        self.vbox.show_all()
        
    def open_browser_and_quit(self,widget,url=None):
        open_browser(widget,url)
        self.respond_done(widget)
        
    def respond_done(self,widget,data=None):
        self.response(gtk.RESPONSE_OK)
        
        
def open_browser(widget,url=None):
    if libpub.HOSTAPP == 'Maemo':
        import osso
        ctx = osso.Context('publishr',libpub.VERSION,False)

    	osso_rpc = osso.Rpc(ctx)
    	osso_rpc.rpc_run("com.nokia.osso_browser","/com/nokia/osso_browser/request",
           	'com.nokia.osso_browser','load_url',rpc_args=(url,))
    else:
        os.system("%s '%s'" % ('firefox', url))
