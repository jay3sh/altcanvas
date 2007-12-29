
    
def handle_crash():
    tb = ''
    for line in traceback.format_exc().split('\n'):
        tb += line+'\n'
        
    envinfo = 'sys.version = <b>%s</b>\n'%sys.version
    envinfo += 'Publishr version = <b>%s</b>'%(HOSTAPP+' '+VERSION)
    crb = CrashReportDialog(envinfo,tb)
    response = crb.run()
    
    if response == gtk.RESPONSE_YES:
        keyserver = xmlrpclib.Server(SERVER)
        keyserver.altcanvas.reportPublishrCrash(envinfo+'\n'+tb)
    # Good to quit the whole plugin app after crash    
            
class CrashReportDialog(gtk.MessageDialog):
    def __init__(self,envinfo,trace):
        msg = '\
<b><big>Sorry!!!</big></b>\n\n\
The publishr plugin has hit an  <b><i>Unknown Exception</i></b>. \
Following is the traceback of the exception. You can help improve this \
plugin by reporting this exception.\n\n\
<b>All you have to do is press <i>"Yes"</i> to report the exception</b>\n\n'
               
        msg += envinfo+'\n\n'
        
        trace = trace.replace('&','&amp;')
        trace = trace.replace('<','&lt;')
        trace = trace.replace('>','&gt;')
        msg += '<span font_family="monospace">'+trace+'</span>'
        gtk.MessageDialog.__init__(self,
                            window,
                            gtk.DIALOG_MODAL|gtk.DIALOG_DESTROY_WITH_PARENT,
                            gtk.MESSAGE_ERROR,
                            gtk.BUTTONS_YES_NO,
                            '')
        self.set_markup(msg) 
        
