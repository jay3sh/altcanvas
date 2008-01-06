#!/usr/bin/python2.5

import os
import gtk
import hildon

def send_rpc(filename):
    import osso
    ctx = osso.Context('publishr_launcher','0.4.0',False)

    osso_rpc = osso.Rpc(ctx)
    osso_rpc.rpc_run("com.altcanvas.publishr","/com/altcanvas/publishr",
        'com.altcanvas.publishr','do_something',
        rpc_args=(filename,))

def spawn_publishr(filename):
    os.spawnlp(os.P_NOWAIT,'python2.5','python2.5',
               '/usr/bin/publishr.py',filename)

if __name__ == '__main__':
    window = hildon.Window()
    #fileChooserDlg = hildon.FileChooserDialog(window,gtk.FILE_CHOOSER_ACTION_OPEN)
    
    fileChooserDlg = gtk.FileChooserDialog('Open picture to publish',window,
                                          gtk.FILE_CHOOSER_ACTION_OPEN,
                                          (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                           gtk.STOCK_OPEN, gtk.RESPONSE_OK))

    resp = fileChooserDlg.run()

    if resp == gtk.RESPONSE_OK:
        spawn_publishr(fileChooserDlg.get_filename())