
from google.appengine.ext import webapp
import google.appengine.api.urlfetch as urlfetch
from google.appengine.ext.webapp.util import run_wsgi_app
import logging

code_url = 'http://altcanvas.googlecode.com/files/'

repo_path = '/dists/testing/main/binary-armel/'
tmp_path = '/binary-armel/'

mime_map = { 
            'deb':'application/x-debian-package',
            'gz':'application/x-gzip'
            }

class FilePipe(webapp.RequestHandler):
    def get(self,filename):
        fetch_headers = {'Cache-Control':'no-cache,max-age=0', 'Pragma':'no-cache'}
        f = urlfetch.fetch(code_url+filename,method=urlfetch.GET,headers=fetch_headers)
        fileext = filename.split('.')[-1]
        self.response.headers['Content-Type'] = mime_map[fileext]
        self.response.headers['Content-Length'] = '%d'%(len(f.content))
        self.response.out.write(f.content)

application = webapp.WSGIApplication(
                     [(repo_path+'(.*)', FilePipe),
                     (tmp_path+'(.*)', FilePipe)],
                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
