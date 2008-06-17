import stackless
from time import sleep

class actor:
    def __init__(self):
        self.channel = stackless.channel()
        self.processMessageMethod = self.defaultMessageAction
        stackless.tasklet(self.processMessage)()

    def processMessage(self):
        while 1:
            self.processMessageMethod(self.channel.receive())
        
    def defaultMessageAction(self,args):
        print args


class Canvas():
    registerChannel = None
    widgets = []
    def __init__(self):
        self.registerChannel = stackless.channel()
        stackless.tasklet(self.register)()

    def register(self):
        while True:
            msg = self.registerChannel.receive()
            print msg


class Widget(actor):
    def __init__(self,channel):
        actor.__init__(self)
        self.registerChannel = channel
        self.registerChannel.send('Register '+self.__class__.__name__)
        #stackless.tasklet(self.registerMe)()

    def registerMe(self):
        self.registerChannel.send('Register '+self.__class__.__name__)

    def sendMessages(self,channel):
        for i in range(1,5):
            channel.send('msg %d'%i)
            stackless.schedule()
            sleep(1)
    

ch1 = stackless.channel()
def send1():
    global ch1  
    for i in range(0,10):
        ch1.send('msg s1 %d'%i)

def send2():
    global ch1  
    for i in range(0,10):
        ch1.send('msg s2 %d'%i)

def listen1():
    global ch1  
    while True:
        print 'l1: '+ch1.receive()

def listen2():
    global ch1  
    while True:
        print 'l2: '+ch1.receive()

if __name__ == '__main__':
    #canvas = Canvas()
    #w = Widget(canvas.registerChannel)

    stackless.tasklet(send1)()
    stackless.tasklet(send2)()
    stackless.tasklet(listen1)()
    stackless.tasklet(listen2)()
    stackless.run()
    

    


