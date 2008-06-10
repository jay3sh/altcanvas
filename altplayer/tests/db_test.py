
import unittest
from db import DB,Record

DB_FILE_NAME='/tmp/test.db'

class TestDB(unittest.TestCase):
    def setUp(self):
        self.db = DB(DB_FILE_NAME)

    def testDB(self):
        class ContactRecord(Record):
            pass
        t1 = ContactRecord(name='Tom Hanks',
                        salary=1000000.90,
                        phone='234-222-0948',
                        email='tom.hanks@hollywood.com',
                        address='1232, Bunker Road, CA-23421')
        t2 = ContactRecord(name='Julia Roberts',
                        salary=1000000.90,
                        phone='214-222-0948',
                        email='julia@hollywood.com',
                        address='1232, Nowhere Road, CA-23421')
        self.db.put(t1)
        self.db.put(t2)

        results = self.db.get(ContactRecord(name='Tom Hanks'))
        self.assertEquals(len(results),1)
        self.assertEquals(results[0].phone,t1.phone)
        results = self.db.get(ContactRecord(salary=1000000.90))
        self.assertEquals(len(results),2)
        self.assert_(t1.name in map(lambda x:x.name,results))
        self.assert_(t2.email in map(lambda x:x.email,results))

    def tearDown(self):
        import os
        os.remove(DB_FILE_NAME)


if __name__ == '__main__':
    for t in [TestDB,]:
        suite = unittest.TestLoader().loadTestsFromTestCase(t)
        testResult = unittest.TextTestRunner(verbosity=2).run(suite)
        
