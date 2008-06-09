
import os
import sqlite3


class Record:
    map = None
    def __init__(self,**kwds):
        self.map = kwds

    def __getattr__(self,elem):
        if elem is 'fieldnames':
            return self.map.keys()
        if elem is 'fieldvalues':
            return self.map.values()
        if elem is 'fieldtypes':
            return map(lambda x: type(x), self.map.values())
        if elem is 'fields':
            return self.map.items()
        if elem in self.map.keys():
            return self.map[elem]

        raise AttributeError("Invalid Attribute '%s'"%elem)

    def __setattr__(self,elem,value):
        if type(elem) != type('string'):
            raise AttributeError("Attribute name has to be a string")

        self.map[elem] = value




class CoverartRecord(Record):
    pass

class DB:
    SQLITE_TYPES = { 
                        type(0):'INTEGER',
                        type(1.0):'REAL',
                        type('string'):'TEXT'
                   }

    def __init__(self,path):
        self.path = path

        self.conn = sqlite3.connect(self.path)
        self.cur = self.conn.cursor()

    def put(self,record):
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

        def quote_strings(s):
            if type(s) == type('string'):
                return '"'+s+'"'
            else:
                return s

        fieldvalues = map(quote_strings,record.fieldvalues)

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

        fields = map(lambda x:x[1], self.cur.fetchall())
        fields = filter(lambda x: x != 'ID',fields)

        return None
        key_str = None

        for key,value in record.fields():
            if key_str:
                key_str += ' and '
            else:
                key_str = ' '
            key_str += ' %s = \"%s\" '%(key,value)

        sql = "select filename,image_url,image_path from coverart where "+key_str

        print sql

        self.cur.execute(sql)

        records = []
        for result in self.cur.fetchall():
            records.append({
                'filename':result[0],
                'image_url':result[1],
                'image_path':result[2]
            })
        return records


if __name__ == '__main__':
    db = DB('/tmp/sample.db')
    '''
    db.put({'filename':' isobel.mp3',
            'image_url':'http://aws.amazon.com/something.jpg',
            'image_path':'/home34343434/.coverart/something.jpg'})
    '''
    print db.get(CoverartRecord(filename='isobel.mp3'))

    '''
    r = CoverartRecord(filename=' isobel.mp3',
            image_url='http://aws.com/something.jpg',
            image_path='/home34343/.coverart/something.jpg')
    db.put(r)
    '''
