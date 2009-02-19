
import unittest

class Element:
    x = 0
    y = 0
    w = 0
    h = 0
    def __init__(self,x,y,w,h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        elem.callback = None

class Canvas:
    xruler = []
    yruler = []

    def __init__(self,(width,height)):
        self.xruler = [[0,width]]

    def reset_ruler(self):
        self.xruler = [[0,width]]

    def register_element(self, elem):
        new_slot = (-1,-1)
        lower_slot = -1
        upper_slot = -1
        for i in range(len(self.xruler)):
            l,u = self.xruler[i]
            if elem.x > u:
                continue
            else:
                if lower_slot < 0:
                    lower_slot = i

            if elem.x+elem.w < u:
                upper_slot = i
            else:
                continue
            
        print 'lower_slot = %d, upper slot = %d'%(lower_slot,upper_slot)
        if lower_slot == upper_slot:
            new_slot = [elem.x,elem.x+elem.w]
            s_low = [self.xruler[lower_slot][0],elem.x-1]
            s_high = [elem.x+elem.w+1,self.xruler[lower_slot][1]]

            del self.xruler[lower_slot]
            self.xruler.insert(lower_slot,s_high)
            self.xruler.insert(lower_slot,new_slot)
            self.xruler.insert(lower_slot,s_low)
        else:
            self.xruler[lower_slot][1] = elem.x - 1
            self.xruler[upper_slot][0] = elem.x+elem.w + 1

            for i in range(upper_slot-lower_slot-1):
                del self.xruler[lower_slot+1]
            
            self.xruler.insert(lower_slot+1,[elem.x,elem.x+elem.w])

        print self.xruler

class TestBasic(unittest.TestCase):
    def setUp(self):
        self.canvas = Canvas((800,480))
        pass

    def testOne(self):
        e = Element(20,40,100,100)
        self.canvas.register_element(e)
        self.canvas.register_element(Element(30,60,100,100))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBasic)
    testResult = unittest.TextTestRunner(verbosity=0).run(suite)
    
