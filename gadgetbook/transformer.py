
import new
from google.appengine.ext import db as gqldb

import schema


class Record:
    __map__ = {}
    def __init__(self,**kwds):
        self.__dict__['__map__'] = kwds

    def __getattr__(self,elem):
        if elem is 'fieldnames':
            return self.__map__.keys()
        if elem is 'fieldvalues':
            return self.__map__.values()
        if elem is 'fieldtypes':
            return __map__(lambda x: type(x), self.__map__.values())
        if elem is 'fields':
            return self.__map__.items()
        if elem in self.__map__.keys():
            return self.__map__[elem]

        raise AttributeError("Invalid Attribute '%s'"%elem)

    def __setattr__(self,elem,value):
        if type(elem) != str:
            raise AttributeError("Attribute name has to be a string")

        if self.__dict__.has_key(elem):
            self.__dict__[elem] = value
            return
        self.__map__[elem] = value

    def dump(self):
        s = '<< %s >>'%self.__class__.__name__
        for k,v in self.__map__.items():
            s = s + '%s : %s'%(k,v)
        return s


def getDB():
    try:
        db = DB()
    except DB,d:
        db = d
    return db

class DB:
    __single__ = None

    def __init__(self):
        if DB.__single__:
            raise DB.__single__
        DB.__single__ = self

    def put(self,record):
        fields = record.__map__
        gql_class = schema.__dict__[record.__class__.__name__]
        gql_object = gql_class(**fields)
        gql_object.put()

    def get(self,record):
        rset = gqldb.GqlQuery("SELECT * FROM "+record.__class__.__name__)
        gql_class = schema.__dict__[record.__class__.__name__]
        records = []
        for r in rset:
            rec = Record()
            for key in gql_class.properties().keys():
                rec.__map__[key] = r.__dict__['_'+key]
            records.append(rec)
        return records
            
        
def getHTML():
    try:
        html = HTML()
    except HTML,html:
        html = html
    return html 


class HTML:
    __single__ = None

    def __init__(self):
        if HTML.__single__:
            raise HTML.__single__
        HTML.__single__ = self

    def generate(self,record):
        html = '<table>'
        for k,v in record.fields:
            html += '<tr><td>'+str(k)+'</td><td>'+str(v)+'</td></tr>'
        html += '</table>'
        return html

