
import gtk

import libpub

import libpub.gui as gui

######################################################
# Control
######################################################
class Control:
    '''
        @summary: This class contains the logic of high level program flow
         - Entry point to the application
         - Callback handlers that respond to user input events
    '''
    def __init__(self,window):
        self.window = window
    
    def entry(self):
        '''
            @summary: Application's entry point
        '''
        #
        # If we remember last service choice, let's skip Home screen
        #
        import libpub
        service_choice = libpub.conf.get('SERVICE_CHOICE')
        if service_choice == 'FLICKR':
            self.flickr_entry_handler(widget=None,data=None)
            return
        elif service_choice == 'PICASAWEB':
            self.picasa_entry_handler(widget=None,data=None)
            return
        
        # No luck, display Home screen
        self.display_home(widget=None,data=None)
            
    def display_home(self,widget,data=None):
        '''
            @summary: Display the home screen that gives a choice between services.
        '''
        gui.empty_window()
        home = gui.Entry(flickr_handler=self.flickr_entry_handler,
              picasa_handler=self.picasa_entry_handler)
        self.window.add(home)
        
    def flickr_entry_handler(self,widget,data=None):
        '''
            @summary: This is called when user chooses to use Flickr.
            
            If we find a saved flickr token:
                proceed straight to upload dialog
            else
                prompt for flickr login information
        '''
        import libpub
        entry = data
        if entry: 
            if entry.remember_service:
                libpub.conf.set('SERVICE_CHOICE','FLICKR')
            else:
                libpub.conf.set('SERVICE_CHOICE',None)
            
        import libpub.flickr
        gui.empty_window()
        
        self.flickr = libpub.flickr.FlickrObject()
        libpub.SERVICE_CHOICE = 'FLICKR'
        
        # If authtoken is found locally, directly go to Upload dialog
        if self.flickr.has_auth():
            self.uploadDlg = gui.UploadDlg(parent=self)
            self.window.add(self.uploadDlg)
        else:
            self.flickrRegBox = gui.FlickrRegisterBox(parent=self)
            self.window.add(self.flickrRegBox)
    
    def picasa_entry_handler(self,widget,data=None):
        '''
           @summary: This is called when user chooses to use Picasaweb
        '''
        import libpub
        entry = data
        if entry:
            if entry.remember_service:
                libpub.conf.set('SERVICE_CHOICE','PICASAWEB')
            else:
                libpub.conf.set('SERVICE_CHOICE',None)
            
        import libpub.picasa
        gui.empty_window()
        
        '''
            @note: PicasawebObject constructor checks for saved username-password
            and tries a login.
            If the login is successful: we will proceed directly to Upload dialog
            
            If it fails: then Login exception will be thrown, which will be 
            handled by the "except" clause will silently handle it and login dialog 
            will be loaded
            
            If no credentials are found in the first place: then the has_auth() will
            return false. The login dialog will be shown after getting out of the try
            block
        '''
        try:
            self.picasa = libpub.picasa.PicasawebObject()
            libpub.SERVICE_CHOICE = 'PICASAWEB'
            # If authtoken is found locally, directly go to Upload dialog
            if self.picasa.has_auth():
                self.uploadDlg = gui.UploadDlg(parent=self)
                self.window.add(self.uploadDlg)
                return
        except Exception, e:
            # Login failed, show the login dialog
            pass
            
        # Either the login failed OR credentials were absent 
        self.picwebRegBox = gui.PicasawebRegisterBox(parent=self)
        self.window.add(self.picwebRegBox)
        
    def flickr_login_handler(self,widget,data=None):
        '''
            @summary: This is called after user has entered Flickr login info
        '''
        gui.empty_window()
        if self.flickr.get_authtoken():
            self.uploadDlg = gui.UploadDlg(parent=self)
            self.window.add(self.uploadDlg)
        else:
            self.window.add(self.flickrRegBox)
        
    def picasa_login_handler(self,widget,data=None):
        '''
            @summary: This is called after user has entered Picasaweb login info
        '''
        gui.empty_window()
        try:
            username = self.picwebRegBox.usernameEntry.get_text()
            password = self.picwebRegBox.passwordEntry.get_text()
            self.picasa.login(username,password)
            
            self.uploadDlg = gui.UploadDlg(parent=self)
            self.window.add(self.uploadDlg)
        
            if self.picwebRegBox.remember_user_check.get_active():
                libpub.conf.set('PICASA_LAST_USERNAME',username)
            else:
                libpub.conf.set('PICASA_LAST_USERNAME',None)
                
            if self.picwebRegBox.remember_pass_check.get_active():
                encpass = libpub.utils.encrypt(password)
                libpub.conf.set('PICASA_LAST_PASSWORD',encpass)
            else:
                libpub.conf.set('PICASA_LAST_PASSWORD',None)
                
            
        except Exception, e:
            libpub.alert('Login error: %s'%e)
            self.window.add(self.picwebRegBox)
    
    def upload(self,widget,data=None):
        '''
            @summary: This is final upload function
        '''
        self.title = self.uploadDlg.titleEntry.get_text()
        buffer = self.uploadDlg.descView.get_buffer()
        startiter,enditer = buffer.get_bounds()
        desc = buffer.get_text(startiter,enditer)
        tags = self.uploadDlg.tagEntry.get_text()
        
        # Get the index of chosen license 
        license_index = self.uploadDlg.licenseCombo.get_active()
            
        # Get the chosen album name
        model = self.uploadDlg.albumCombo.get_model()
        active = self.uploadDlg.albumCombo.get_active()
        if active < 0:
            curalbum = self.uploadDlg.albumCombo.get_active_text()
        else:
            curalbum = model[active][0]
            
        # Upload to Flickr
        if libpub.SERVICE_CHOICE == 'FLICKR':
            
            from libpub.flickr import FlickrException
            
            # Get license ID for chosen license
            if license_index > 0 and license_index < len(libpub.LicenseList):
                license_id = libpub.LicenseList[license_index][0]
            else:
                license_id = 0
                
            try:
                if len(libpub.filename_list) == 1:
                    # Upload the photo
                    url = self.flickr.upload(
                        filename = libpub.filename_list[0],
                        title = self.title,
                        description = desc,
                        is_public = self.uploadDlg.is_public,
                        tags = tags,
                        license_id = str(license_id),
                        photoset = curalbum)
                    if url:
                        # save the current album into config file
                        libpub.conf.set('FLICKR_LAST_PHOTOSET',curalbum)
                    	libpub.conf.set('LAST_PRIVACY_CHOICE',self.uploadDlg.is_public)
                    	libpub.conf.set('LAST_LICENSE_USED',license_index)
            
                    	# success message
                    	#libpub.alert("Image upload was successful.\n(Flickr URL: %s)"%url,
                    	#         gtk.MESSAGE_INFO)
                    	successDlg = gui.SuccessDialog(url)
                    	successDlg.run()
                else:
                    count = 0
                    total = len(libpub.filename_list)
                    for filename in libpub.filename_list:
                        url = self.flickr.upload(
                            filename = filename,
                            title = self.title+'(%d of %d)'%(count+1,total),
                        	description = desc+'(%d of %d)'%(count+1,total),
                        	is_public = self.uploadDlg.is_public,
                        	tags = tags,
                        	license_id = str(license_id),
                            photoset = curalbum)
                        count+=1
                        
                        if not url:
                            raise Exception('Upload of Image %d of %d failed'%
                                            (count,total))
                            
                    libpub.alert("Image upload of %d images was successful!"%total, 
                                 gtk.MESSAGE_INFO)
                
                
            except FlickrException, fe:
                libpub.alert("Flickr Exception: %s"%fe)
                
            except Exception, e:
                libpub.alert("Upload exception: %s"%e)
                
            
        # Upload to Picasaweb
        elif libpub.SERVICE_CHOICE == 'PICASAWEB':
                
            from libpub.gdata.photos.service import PicasaException
            success = False
            
            if curalbum == None or curalbum.strip() == '':
                libpub.alert('Picasaweb doesn\'t support uploading photos \
without an album. If you don\'t have any album already, create one by typing \
a new album name in the "Albums" entry.')
                return
            
            if self.title == None or self.title.strip() == '':
                libpub.alert('Title cannot be empty')
                return
                
            # Determine the license text
            # Ignore the blank-license index 
            if license_index > 0 and license_index < len(libpub.LicenseList)-1:
                license_text = libpub.LicenseList[license_index][1]
                license_url = libpub.LicenseList[license_index][2]
                desc += '  [%s]'%(license_text)
                
            # this is the blank-index choice, preserve it
            elif license_index == len(libpub.LicenseList):
                pass
            
            # correct invalid values, it is possible for user entered text
            else:
                license_index = 0
                
            try:
                if len(libpub.filename_list) == 1:
                    success = self.picasa.upload(
                        filename = libpub.filename_list[0], 
                        title = self.title,
                        summary = desc,
                        tags = tags,
                		album = curalbum)
                else:
                    count = 0
                    total = len(libpub.filename_list)
                    for filename in libpub.filename_list:
                        success = self.picasa.upload(
                            filename = filename,
                            title = self.title+'(%d of %d)'%(count+1,total), 
                            summary = desc+'(%d of %d)'%(count+1,total), 
                            tags = tags,
                		    album = curalbum)
                        count+=1
                        
                        if not success:
                            raise Exception('Upload of Image %d of %d failed'%
                                        (count,total))
                        
                    
            except PicasaException, pe:
                libpub.alert('Picasa Exception: %s'%pe)
            
            except Exception, e:
                libpub.alert('Upload exception: %s'%e)
                
            if success:
                # save the current album into config file
                libpub.conf.set('PICASA_LAST_ALBUM',curalbum)
            	libpub.conf.set('LAST_LICENSE_USED',license_index)
                libpub.alert('Successful upload to Picasaweb!',gtk.MESSAGE_INFO)
            
        # Cleanup the GUI
        libpub.destroy()
