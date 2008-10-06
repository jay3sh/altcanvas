
from google.appengine.ext import db

class Gadget(db.Model):
    name = db.StringProperty()
    manufacturer = db.StringProperty()
    processor = db.StringProperty()
    memory = db.StringProperty()
    display = db.StringProperty()
    url = db.StringProperty()

