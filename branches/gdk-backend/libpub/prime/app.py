
# This file is part of AltCanvas.
#
# http://code.google.com/p/altcanvas
#
# AltCanvas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AltCanvas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AltCanvas.  If not, see <http://www.gnu.org/licenses/>.



import os 
import cairo
from libpub.prime.widgets.image import Image
from libpub.prime.widgets.pad import Pad 
from libpub.prime.widgets.label import Label 
from libpub.prime.widget import WidgetWrapper
import libpub.prime.mask as mask
from libpub.prime.widgets.fancyentry import FancyEntry 
from libpub.prime.widgets.entry import Entry 
from libpub.prime.utils import get_image_locations,get_uniform_fit, \
    LAYOUT_STEP, LAYOUT_UNIFORM_OVERLAP,LAYOUT_UNIFORM_SPREAD, open_browser, \
    detect_platform,RGBA,html2rgb,log,recalculate_clouds
from libpub.prime.animation import Path
from libpub.prime.widgetq import WidgetQueue
from libpub.prime.layer import Layer,ImageLayer,InputLayer, \
                        ButtonLayer, PublishLayer, ListPickerLayer, \
                        MessageLayer

import libpub
import libpub.flickr_local as flickr
import libpub.picasa as picasa
            
class App:
    
    surface = None
    ctx = None
    
    
    app_width = 800
    app_height = 480
    
    def __init__(self):
        # Setup cairo surface and context
        self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32,
                                          self.app_width,self.app_height)
        self.ctx = cairo.Context(self.surface)
        
        self.layers = []
        
        
        
    def redraw(self):
        # Create Image widgets for images and lay them out on the surface
        self.ctx.rectangle(0,0,self.app_width,self.app_height)
        self.ctx.set_source_rgba(0,0,0,1)
        self.ctx.fill()
        
        for i in range(len(self.layers)):
            self.layers[i].redraw(self.ctx)
        
        
    def adjust_clouds(self):
        widgetQ = []
        for layer in self.layers:
            widgetQ += layer.widgetQ.widgetQ
        recalculate_clouds(widgetQ)

    def dispatch_key_event(self,keyval,state):
        for layer in self.layers:
            layer.key_listener(keyval,state)
                
    def dispatch_pointer_event(self,x,y,pressed):
        for layer in self.layers:
            layer.pointer_listener(x,y,pressed)
                
            
            
class PublishrApp(App):
    
    inputPad = None
    background = None
    bg_ignore_count = 0
    px = 0
    py = 0
    
    imageLayer = None
    buttonLayer = None
    inputLayer = None
    publishLayer = None
    
    def __init__(self):
        App.__init__(self)
        
        # Other initialization
        libpub.start_prime()
        self.flickr = flickr.FlickrObject()
        self.picasa = picasa.PicasawebObject()
            
        
        self.imageLayer = ImageLayer(app=self,isVisible=True)
        self.layers.append(self.imageLayer)
        
        self.buttonLayer = ButtonLayer(app=self,isVisible=True)
        self.layers.append(self.buttonLayer)

        if not self.flickr.has_auth():
            #self.buttonLayer.publishButton.text = 'Sign In'
            self.buttonLayer.publishButton.redraw()
            
        self.adjust_clouds()
        libpub.prime.canvas.redraw()
        
        
            
        
        
    def on_background_tap(self,pad):
        # Remove the input pad from widgetQ
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        if self.inputLayer in self.layers:
            
            self.inputLayer.save_image_info()
            self.inputLayer.clear_widgets()
            
            ipx = self.px + int(self.app_width/20)
            ipy = self.py + int(self.app_height/3 - 
                                self.inputLayer.imageOnPad.widget.h/2)
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy)
            pathOut.add_stop(self.inputLayer.imageOnPad.x,
                             self.inputLayer.imageOnPad.y)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
            for i in range(NUM_STEPS):
                if i == 0:
                    self.inputLayer.remove_widget(pathOut.widget)
            
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                
                    self.inputLayer.imageOnPad = None
                    self.layers.remove(self.inputLayer)
                else:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
                self.adjust_clouds()
                libpub.prime.canvas.redraw()
                
        if self.publishLayer in self.layers:
            self.publishLayer.clean_widgets()
            self.layers.remove(self.publishLayer)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
            
                
    def on_image_click(self,image):
            
        if image.url:
            open_browser(image.url)
            return
        
        if self.inputLayer == None:
            self.inputLayer = InputLayer(app=self,image_dim=(image.w,image.h))
            
        if self.inputLayer not in self.layers:
            self.layers.append(self.inputLayer)
            
        ipx = self.inputLayer.ipx
        ipy = self.inputLayer.ipy
        
        if detect_platform() == 'Nokia':
            NUM_STEPS = 3
        else:
            NUM_STEPS = 13 
            
        #inComing
        pathIn = Path(image)
        imageW = self.imageLayer.get_widget(image)
        if not imageW:
            # This means that this handler got called while
            # another one was already in the middle of an animation
            # and had removed this image widget from the imageLayer queue
            # It is safe to ignore and stop this handler
            return
        pathIn.add_start(imageW.x,imageW.y)
        pathIn.add_stop(ipx,ipy)
        pathIn.num_steps = NUM_STEPS 
        pathInPoints = pathIn.get_points()
        
        pathOut = None
        #outGoing
        if self.inputLayer.imageOnPad:
            self.inputLayer.save_image_info()
            self.inputLayer.clear_widgets()
            pathOut = Path(self.inputLayer.imageOnPad.widget)
            pathOut.add_start(ipx,ipy)
            pathOut.add_stop(self.inputLayer.imageOnPad.x,self.inputLayer.imageOnPad.y)
            pathOut.num_steps = NUM_STEPS
            pathOutPoints = pathOut.get_points()
            
        # replace the outgoing image with new one
        self.inputLayer.imageOnPad = self.imageLayer.get_widget(image)
            
        for i in range(NUM_STEPS):
            if i == 0:
                # In first step switch the images from their
                # existing layer to the destination layer
                self.imageLayer.remove_widget(pathIn.widget)
                ww = pathInPoints[i]
                self.inputLayer.add_widget(ww)
                
                if pathOut:
                    self.inputLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            elif i == NUM_STEPS-1:
                # In the last step remove the widgets in motion
                # and draw the final layers with their own widget
                # arrangements
                self.inputLayer.remove_widget(pathIn.widget)
                self.inputLayer.show_image()
                
                # TODO: for outgoing widget need to call imageLayers's
                # function
                if pathOut:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            else:
                self.inputLayer.remove_widget(pathIn.widget)
                ww = pathInPoints[i]
                self.inputLayer.add_widget(ww)
                
                if pathOut:
                    self.imageLayer.remove_widget(pathOut.widget)
                    ww = pathOutPoints[i]
                    self.imageLayer.add_widget(ww)
                    
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        
    def on_import_clicked(self,importButton):
        importButton.disable_pointer_listener()
        import gtk
        if detect_platform() == 'Nokia':
            import hildon
            fileChooserDlg = hildon.FileChooserDialog(
                            libpub.prime.canvas,
                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        else:
            fileChooserDlg = gtk.FileChooserDialog('Open picture to publish',
                            libpub.prime.canvas,
                            gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                             gtk.STOCK_OPEN, gtk.RESPONSE_OK))
            
        resp = fileChooserDlg.run()
    
        path = None
        if resp == gtk.RESPONSE_OK:
            path = fileChooserDlg.get_filename()
            
        fileChooserDlg.destroy()
        
        images = []
        if path:
            if os.path.isdir(path):
                files = os.listdir(path)
                for f in files:
                    if f.lower().endswith('jpg') or  \
                        f.lower().endswith('jpeg') or  \
                        f.lower().endswith('png') or  \
                        f.lower().endswith('gif'):
                            images.append(path+os.sep+f)
            else:
                images.append(path)
            
            self.imageLayer.display_images(images)
            
        importButton.reset_focus()
        importButton.enable_pointer_listener()
        
    def on_quit_clicked(self,widget):
        import gtk
        gtk.main_quit()
    
    def on_publish_clicked(self,widget):
        
        if not self.publishLayer:
            self.publishLayer = PublishLayer(app=self)
        
        if self.publishLayer not in self.layers:
            self.layers.append(self.publishLayer)
            
            self.publishLayer.opening_layout()
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
            
    def refresh_load_status(self,done,total):
        self.buttonLayer.refresh_status('Loading ',done, total)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()
        
    def refresh_upload_status(self,done,total):
        self.buttonLayer.refresh_status('Upload done ',done, total)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()
        
    def on_flickr_clicked(self,widget):
        if self.flickr.has_auth():
            self.publishLayer.prompt_final_upload(self.flickr)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        else:
            if not self.publishLayer:
                self.publishLayer = PublishLayer(app=self)
            if self.publishLayer not in self.layers:
                self.layers.append(self.publishLayer)
            self.publishLayer.prompt_flickr_auth_1()
            self.adjust_clouds()
            libpub.prime.canvas.redraw()

    def on_picasa_clicked(self,widget):
        if self.picasa.has_auth():
            self.publishLayer.prompt_final_upload(self.picasa)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        else:
            if not self.publishLayer:
                self.publishLayer = PublishLayer(app=self)
            if self.publishLayer not in self.layers:
                self.layers.append(self.publishLayer)
            self.publishLayer.prompt_picasa_auth()
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        
    def on_flickr_authorize(self,widget):
        if not self.flickr.has_auth():
            url = self.flickr.get_authurl()
            if detect_platform() == 'Nokia':
                libpub.prime.canvas.unmaximize()
            open_browser(url[0])
            self.publishLayer.prompt_flickr_auth_2()
            
    def on_flickr_authdone(self,widget):
        success = self.flickr.get_authtoken()
            
        if success:
            self.publishLayer.prompt_final_upload(self.flickr)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()

        
    def on_picasa_authorize(self,widget):
        try:
            self.picasa.login(
                    self.publishLayer.picasaUsernameEntry.text,
                    self.publishLayer.picasaPasswordEntry.text,
                    save=True)
            self.publishLayer.clean_widgets()
        except libpub.gdata.service.BadAuthentication, bae:
            libpub.alert('Invalid username or password')
            return

        if self.picasa.has_auth():
            self.publishLayer.prompt_final_upload(self.picasa)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()
        
            
    def on_pick_album(self,widget):
        albums = widget.data

        # TODO: remove hardcoding
        ew = 200
        eh = 35
        ex = self.app_width/2 - ew/2 + 10
        ey = self.app_height/2 - eh/2 + 10
        self.lplayer = ListPickerLayer(app=self,optionList=albums,
            entry_dim=(ex,ey,ew,eh))

        self.layers.append(self.lplayer)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()

    def on_album_picked(self,widget):
        self.publishLayer.albumEntry.text = widget.data
        self.publishLayer.albumEntry.redraw()
        if self.lplayer in self.layers:
            self.layers.remove(self.lplayer)
            self.adjust_clouds()
            libpub.prime.canvas.redraw()

    def final_upload(self,widget):
        albumName = self.publishLayer.albumEntry.text
        if albumName == 'New or Pick one...':
            libpub.alert('Choose a valid album/photoset')
            return

        self.publishLayer.clean_widgets()
        self.layers.remove(self.publishLayer)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()

        self.imageLayer.upload(
                widget.data,                        # service
                albumName)

    def signOut(self,widget):
        service = widget.data

        if isinstance(service,libpub.picasa.PicasawebObject):
            libpub.conf.set('PICASA_LAST_USERNAME',None)
            libpub.conf.set('PICASA_LAST_PASSWORD',None)
            self.picasa = picasa.PicasawebObject()
        else:
            libpub.conf.set('FLICKR_TOKEN',None)
            self.flickr = flickr.FlickrObject()

        self.publishLayer.clean_widgets()
        self.layers.remove(self.publishLayer)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()

    def on_password_help(self,widget):
        self.mlayer = MessageLayer(app=self,focus=(400,240))
        self.layers.append(self.mlayer)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()
        
    def cleanup_message(self,widget):
        self.layers.remove(self.mlayer)
        self.adjust_clouds()
        libpub.prime.canvas.redraw()
