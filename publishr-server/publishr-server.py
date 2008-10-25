from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from xmlrpcserver import XmlRpcServer

import xmlrpclib
import logging

from flickrinterface import getAltCanvasXmlRpc
import traceback


class XMLRpcHandler(webapp.RequestHandler):
    rpcserver = None
    
    def __init__(self):
        self.rpcserver = XmlRpcServer()
        flickr = getAltCanvasXmlRpc()
        self.rpcserver.register_class('altcanvas',flickr)

    def post(self):
        try:
            self.rpcserver.handle(self)
        except Exception, e:
            logging.error('Post: '+str(e))

application = webapp.WSGIApplication(
                                     [('/xmlrpc/', XMLRpcHandler)],
                                     debug=True)
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
    main()
