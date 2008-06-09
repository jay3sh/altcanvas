
import os
import sqlite3


class Record:
    map = None
    def __init__(self,**kwds):
        self.map = kwds

    def __getattr__(self,elem):
        if elem in self.map.keys():
            return self.map[elem]

class CoverartRecord(Record):
    pass

class DB:

    def __init__(self,path):
        self.path = path

        if not os.access(self.path,os.W_OK):
            self.conn = sqlite3.connect(self.path)
            self.cur = self.conn.cursor()
            self.cur.execute("create table coverart (ID INTEGER PRIMARY KEY, filename TEXT, image_url TEXT, image_path TEXT)")
            self.conn.commit()
        else:
            self.conn = sqlite3.connect(self.path)
            self.cur = self.conn.cursor()

    def put(self,record):
        self.cur.execute("insert into coverart(filename,image_url,image_path) values(\"%s\",\"%s\",\"%s\")"%(
                            record['filename'],record['image_url'],record['image_path']))
        self.conn.commit()

    def get(self,record):
        key_str = None

        print record.items()

        for key,value in record.items():
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
    #db = DB('/tmp/sample.db')
    '''
    db.put({'filename':' isobel.mp3',
            'image_url':'http://aws.amazon.com/something.jpg',
            'image_path':'/home34343434/.coverart/something.jpg'})
    '''
    #print db.get({'filename': ' isobel.mp3'})
    r = CoverartRecord(filename=' isobel.mp3',
            image_url='http://aws.amazon.com/something.jpg',
            image_path='/home34343434/.coverart/something.jpg')
    print r.filename
