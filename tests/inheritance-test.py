#!/usr/bin/python

class Widget:
    w = 0
    h = 0
    clouds = []
    
    def __init__(self,w,h):
        self.w = w
        self.h = h
    
class Image(Widget):
    def __init__(self,w,h):
        Widget.__init__(self,w,h)
        
class Pad(Widget):
    def __init__(self,w,h):
        Widget.__init__(self,w,h)

i = Image(10,10)
i.clouds.append(1)
print '%d, %d'%(i.w,i.h)
print i.clouds

print '---'
p = Pad(20,20)
p.w = 30
p.h = 30
p.clouds = []
p.clouds.append(3)
print '%d, %d'%(i.w,i.h)
print '%d, %d'%(p.w,p.h)
print i.clouds
print p.clouds
