#!/usr/bin/python2.5

import os
import gtk
#import hildon

def send_rpc(filename):
    import osso
    ctx = osso.Context('publishr_launcher','0.4.0',False)

    osso_rpc = osso.Rpc(ctx)
    osso_rpc.rpc_run("com.altcanvas.publishr","/com/altcanvas/publishr",
        'com.altcanvas.publishr','do_something',
        rpc_args=(filename,))


class MultiChoiceDialog(gtk.Dialog):
    RESPONSE_SINGLE = -100
    RESPONSE_MULTI = -101
    def __init__(self):
        gtk.Dialog.__init__(self,'Publishr')
        
        label = gtk.Label('Upload choice')
        singleButton = gtk.Button('Single Image upload')
        singleButton.connect('clicked',lambda dlg: self.response(self.RESPONSE_SINGLE))
        multiButton = gtk.Button('Mass Image upload')
        multiButton.connect('clicked',lambda dlg: self.response(self.RESPONSE_MULTI))
        quitButton = gtk.Button('Quit')
        quitButton.connect('clicked',lambda dlg: self.response(gtk.RESPONSE_CANCEL))
        
        self.vbox.pack_start(label)
        self.vbox.pack_start(singleButton)
        self.vbox.pack_start(multiButton)
        self.vbox.pack_start(quitButton)
        
        self.vbox.set_spacing(10)
        self.vbox.show_all()
        
        
def spawn_publishr(filename):
    os.spawnlp(os.P_NOWAIT,'python2.5','python2.5',
               'publishr.py',filename)

if __name__ == '__main__':
    
    window = gtk.Window()
    #window = hildon.Window()
    
    mdlg = MultiChoiceDialog()
    resp = mdlg.run()
    
    if resp == mdlg.RESPONSE_SINGLE:
        #fileChooserDlg = hildon.FileChooserDialog(
        #                    window,gtk.FILE_CHOOSER_ACTION_OPEN)
        fileChooserDlg = gtk.FileChooserDialog('Open picture to publish',window,
                                          gtk.FILE_CHOOSER_ACTION_OPEN,
                                          (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN, gtk.RESPONSE_OK))
        
    elif resp == mdlg.RESPONSE_MULTI:
        #fileChooserDlg = hildon.FileChooserDialog(
        #                    window,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
        fileChooserDlg = gtk.FileChooserDialog('Open picture to publish',window,
                                          gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,
                                          (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN, gtk.RESPONSE_OK))
    
    resp = fileChooserDlg.run()
    
    if resp == gtk.RESPONSE_OK:
        spawn_publishr(fileChooserDlg.get_filename())    
    

