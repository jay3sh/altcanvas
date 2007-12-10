'''publishr plugin library '''

import os
import gtk

window = None
config = None
filename = '/tmp/test123.jpg'
CONFIG_FILE = ''

SERVER = 'http://fog.altcanvas.com/xmlrpc/'
VERSION = '0.2'

        
def alert(msg,type=gtk.MESSAGE_ERROR):
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()
    
def load_authtoken():
    try:
        f = open(CONFIG_FILE,'r')
    except IOError, ioe:
        return None
    authtoken = f.readline()
    return authtoken

def save_authtoken(authtoken=None):
    try:
        f = open(CONFIG_FILE,'w')
    except IOError, ioe:
        alert("Error saving Flickr account info. "+
              "Please check that your home directory is writable to this application")
        return None
    f.write(authtoken)
    f.close()

def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()

def signout(widget=None,data=None):
    # Check if the file exists
    try:
        os.stat(CONFIG_FILE)
    except OSError, oe:
        return
    # Yes, it exists, delete it now
    try:
        os.remove(CONFIG_FILE)
    except IOError, ioe:
        alert('Error deleting flickr token. Check permissions on %s'%CONFIG_FILE)
    # Quit the GUI
    destroy()
