#!/usr/bin/env python2.5
import gtk
import hildon

#from threading import Thread
#
#class Importer(Thread):
#    def __init__(self):
#        Thread.__init__(self)
#        
#    def run(self):
#        import libpub
#        import libpub.gui


class PublishrApp(hildon.Program):
  bg_importer = None
  def __init__(self):
    hildon.Program.__init__(self)

    self.window = hildon.Window()
    self.window.connect("destroy", gtk.main_quit)
    self.add_window(self.window)


  def loadPublishr(self,filename):
    #if self.bg_importer:
    #    self.bg_importer.join()
        
    print "[PublishrApp] Loading libpub: %s"%time.asctime()
    import libpub
    import libpub.gui
    print "[PublishrApp] Done loading libpub: %s"%time.asctime()
    libpub.config = libpub.Config()
    libpub.window = self.window
    libpub.filename = filename
    libpub.window.connect("delete_event",libpub.delete_event)
    libpub.window.connect("destroy",libpub.destroy)
    gui = libpub.gui.UploadGUI()
    self.window.show_all()


  def selectPhoto(self):
    #self.fileChooser = gtk.FileChooserDialog(
    #    title="Choose a photo to publish",
    #    buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, 
    #             gtk.STOCK_OK, gtk.RESPONSE_OK))
    
    self.fileChooser = hildon.FileChooserDialog(
                        self.window,gtk.FILE_CHOOSER_ACTION_OPEN)

    response = self.fileChooser.run()
    
    if response == gtk.RESPONSE_OK:
        filename = self.fileChooser.get_filename()
        self.fileChooser.destroy()
        self.loadPublishr(filename)
        return True
    else:
        self.fileChooser.destroy()
        return False

  def run(self):
    gtk.main()
    
  def open_browser(self,url):
    import osso
    ctx = osso.Context('publishr','0.0.1',False)

    osso_rpc = osso.Rpc(ctx)
    osso_rpc.rpc_run("com.nokia.osso_browser","/com/nokia/osso_browser/request",
       'com.nokia.osso_browser','load_url',rpc_args=('http://www.flickr.com/',))

    
if __name__ == "__main__":
    #import osso
    #ctx = osso.Context('publishr','0.0.1',False)
    #browserapp = osso.Application(ctx)
    #browserapp.application_top("browser")
    app = PublishrApp()
    
    #app.bg_importer = Importer()
    #app.bg_importer.start()

    if app.selectPhoto():
        app.run()
