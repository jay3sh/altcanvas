
import os
import sqlite3


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
        print '<< %s >>'%self.__class__.__name__
        for k,v in self.__map__.items():
            print '%s : %s'%(k,v)
        print ''


class CoverartRecord(Record):
    pass

def getDB(dbfilename):
    try:
        db = DB(dbfilename)
    except DB,d:
        db = d
    return db

class DB:
    __single__ = None
    SQLITE_TYPES = { 
                        int:'INTEGER',
                        float:'REAL',
                        str:'TEXT'
                   }

    def __init__(self,path):
        if DB.__single__:
            raise DB.__single__

        DB.__single__ = self

        self.path = path

        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()

    def __quote_strings__(self,s):
        if type(s) == str:
            return '"'+s+'"'
        else:
            return s

    def put(self,record):
        if not record.fieldvalues:
            raise Exception('Creating empty records is not supported')

        self.cur.execute("select name from sqlite_master where type='table'")
        tables = map(lambda x: x[0],self.cur.fetchall())

        tablename = record.__class__.__name__

        if tablename not in tables:
            # Create a new table for this type of record
            sql = 'create table %s '%tablename
            sql += '(ID INTEGER PRIMARY KEY '

            for field in record.fields:
                sql += ',%s %s'%(field[0],self.SQLITE_TYPES[type(field[1])])

            sql += ')'

            self.cur.execute(sql)
            self.conn.commit()

        fieldvalues = map(self.__quote_strings__,record.fieldvalues)

        # Now insert the record fields into the database
        sql = 'insert into %s'%tablename
        sql += '('
        sql += reduce(lambda x,y: '%s,%s'%(x,y), record.fieldnames)
        sql += ')'
        sql += ' values '
        sql += '('
        sql += reduce(lambda x,y: '%s,%s'%(x,y), fieldvalues)
        sql += ')'

        self.cur.execute(sql)
        self.conn.commit()

    def get(self,record):
        tablename = record.__class__.__name__

        # Get all the field names from table info
        sql = 'pragma table_info(%s)'%tablename

        self.cur.execute(sql)

        fieldnames = map(lambda x:x[1], self.cur.fetchall())

        if not fieldnames:
            return []

        fieldnames = filter(lambda x: x != 'ID',fieldnames)


        sql = 'select '
        if fieldnames:
            sql += reduce(lambda x,y: '%s,%s'%(x,y), fieldnames)
        else:
            sql += '*'
        sql += ' from '+tablename

        if record.fieldvalues:

            sql += ' where '

            fieldvalues = map(self.__quote_strings__,record.fieldvalues)

            fields = map(None,record.fieldnames,fieldvalues)
    
            conditions = map(lambda x: '%s = %s'%x , fields)
    
            condition_str = reduce(lambda x,y: '%s and %s'%(x,y), conditions) 
            
            sql += condition_str

        self.cur.execute(sql)

        results = self.cur.fetchall()

        records = []
        for result in results:
            r = Record()
            r.__class__ = record.__class__
            for key,value in map(None,fieldnames,result):
                r.__setattr__(str(key),value)
            records.append(r)
            
        return records


if __name__ == '__main__':
    import sys
    db = DB(sys.argv[1])


    r = CoverartRecord(filename=' isobel.mp3',
            image_url='http://aws.com/something.jpg',
            image_path='/home34343/.coverart/something.jpg')
    db.put(r)


    for r in db.get(CoverartRecord(filename=' isobel.mp3')):
        r.dump()
        
