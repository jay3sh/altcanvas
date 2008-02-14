#!/usr/bin/python2.5

import sys
import os
import gtk

    
#def rpc_callback(interface, method, arguments, user_data):
def flash_msg(msg):
    import osso
    osso_c = osso.Context("publishr", "0.4.0", False)
    osso_sysnote = osso.SystemNote(osso_c)
    osso_sysnote.system_note_infoprint(msg)

    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "filename argument missing"
        sys.exit(1)
        
    path = sys.argv[1]
    images = []
    if os.path.isdir(path):
        files = os.listdir(path)
        for f in files:
            if f.lower().endswith('jpg') or  \
                f.lower().endswith('jpeg') or  \
                f.lower().endswith('gif'):
                    images.append(path+os.sep+f)
    else:
        images.append(path)
        
    #flash_msg("Loading publishr")
    import libpub
    try:
        import hildon
    except ImportError, ie:
        libpub.start(hostapp='Desktop',fnames=images)
    else:
        libpub.start(hostapp='Maemo',fnames=images,guiwindow=hildon.Window())
        
    gtk.main()
    
#    
#    osso_c = osso.Context("publishr", "0.4.0", False)
#    print "publishr started"
#    osso_rpc = osso.Rpc(osso_c)
#    osso_rpc.set_rpc_callback("com.altcanvas.publishr",
#        "/com/altcanvas/publishr",
#        "com.altcanvas.publishr", callback_func, osso_c)
