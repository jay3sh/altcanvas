from google.appengine.ext import db as gqldb
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import os
from google.appengine.ext.webapp import template

from transformer import Record,getDB,getHTML

class Gadget(Record):
    pass

class Main(webapp.RequestHandler):
    def get(self):
        form = \
        """
        <html>
            <title>
                Search GadgetBook
            </title>
            <body>
                <form action="/search" method="get">
                    <input name="search" type="text"/> <br>
                    <input type="submit" value="Search"/>
                </form>
            </body>
        </html>
        """
        self.response.out.write(form)

class Enter(webapp.RequestHandler):
    def get(self):
        form = \
        """
        <html>
            <title>
                Enter Gadget info
            </title>
            <body>
                <h1>Enter Gadget information</h1>
                <form action="/save" method="post">
                Name: <br>
                <input name="name" type="text"/> <br>
                Manufacturer: <br>
                <input name="manufacturer" type="text"/> <br>
                Processor: <br>
                <input name="processor" type="text"/> <br>

                Display: <br>
                <input name="display" type="text"/> <br>

                <input type="submit" value="Save"/>
                </form>
            </body>
        </html>
        """
        self.response.out.write(form)

class Save(webapp.RequestHandler):
    def post(self):
        name = self.request.get('name')
        manufacturer = self.request.get('manufacturer')
        processor = self.request.get('processor')
        display = self.request.get('display')
        gdgt = Gadget(
                    name=name,
                    vendor=manufacturer,
                    processor=processor,
                    display=display,
                    url=None)
        getDB().put(gdgt)

class Search(webapp.RequestHandler):
    def get(self):
        #search = self.request.get('search')
        s = '<br>'
        gadgets = getDB().get(Gadget())

        for gadget in gadgets:
            s += getHTML().generate(gadget)
            s += '<br>'

        self.response.out.write('<html><body>Searching:<pre>')
        self.response.out.write(s)
        self.response.out.write('</pre></body></html>')

application = webapp.WSGIApplication(
                 [
                    ('/',       Main),
                    ('/enter',  Enter),
                    ('/save',   Save),
                    ('/search', Search),
                 ],
                 debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

