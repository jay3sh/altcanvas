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


class Widget(actor):
    def __init__(self,channel):
        actor.__init__(self)
        self.registerChannel = channel
        self.registerChannel.send((self,10,10,100,100))

        self.evtchl = stackless.channel()
        stackless.tasklet(self.onClick)()

    def onClick(self):
        while True:
            print self.evtchl.receive()

    def sendMessages(self,channel):
        for i in range(1,5):
            channel.send('msg %d'%i)
            stackless.schedule()
            sleep(1)
    

import canvasX
class Canvas:
    widget_list = []
    def __init__(self):
        self.registerChl = stackless.channel()
        stackless.tasklet(self.register)()
        canvasX.create()
        canvasX.register_motion_handler(self)

    def register(self):
        while True:
            widget = self.registerChl.receive()
            print widget
            self.widget_list.append(widget)
        
    def motion_handler(self,x,y):
        def deliever_event(widget):
            wdt,x0,y0,w,h = widget
            if (x>x0 and x<x0+w and y>y0 and y<y0+h):
                wdt.evtchl.send('CLICK')

        map(deliever_event,self.widget_list)
            

    def run(self):
        canvasX.run()


if __name__ == '__main__':

    canvas = Canvas()

    w = Widget(canvas.registerChl)

    '''
    stackless.tasklet(send1)()
    stackless.tasklet(send2)()
    stackless.tasklet(listen1)()
    stackless.tasklet(listen2)()
    '''
    stackless.run()
    canvas.run()
    

    


