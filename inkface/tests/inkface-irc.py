#!/usr/bin/env python

import os
import sys
import inkface
import socket
import threading

canvas = None

IRC_SVG=sys.argv[1]
exit_sign = False
statusBar = None
irc = None

msglist = []
msgtxtlist = [None,None,None,None,None]

def msghandler(nick,msg):
    global msgtxtlist
    global msglist
    
    clean_msg = nick+': '+msg.strip()
    final_msg = clean_msg[:70]+'\n'+clean_msg[70:140]+'\n'+clean_msg[140:210]
    msglist =  [final_msg] + msglist
    if(len(msglist) > 5):
        msglist = msglist[:-1]

    for i in range(len(msgtxtlist)):
        if i < len(msglist):
            if i == 0:
                msgtxtlist[i].text = msglist[i]
            elif i == 1:
                msgtxtlist[i].text = msglist[i][:140]
            elif i == 1:
                msgtxtlist[i].text = msglist[i][:60]
            else:
                msgtxtlist[i].text = msglist[i][:40]+'...'
                
            msgtxtlist[i].refresh()
        
    canvas.refresh()

def onReportStatus(status):
    global statusBar
    global canvas
    statusBar.text = status 
    statusBar.refresh()
    canvas.refresh()
    
def onMsgboxDraw(elem):
    global canvas
    i = int(elem.name[6])
    if(i == 0 or i < len(msglist)):
        canvas.draw(elem)

def onExitGlowDraw(e):
    global canvas
    if e.opacity:
        canvas.draw(e)

def onExit(elem,elist):
    from time import sleep
    for e in elist:
        if e.name == 'exitButtonGlow':
            e.opacity = 1
            canvas.refresh()
            break
    global exit_sign
    exit_sign = True
    irc.join()
    inkface.exit()

def main():
    global canvas
    global msgtxtlist
    global statusBar
    global irc

    irc_network = 'irc.freenode.net'
    irc_channel = 'ubuntu'


    elements = inkface.loadsvg(IRC_SVG)
    canvas = inkface.create_X_canvas()
    canvas.register_elements(elements)

    # Wire the handlers and init elements
    for el in elements:
        if el.name.startswith('msgtxt'):
            i = int(el.name[6])
            msgtxtlist[i] = el
            el.text = ''
            el.refresh()

        if el.name.startswith('msgbox'):
            el.onDraw = onMsgboxDraw

        if el.name == 'networkName':
            statusBar = el
        if el.name == 'channelName':
            el.text = irc_channel
            el.refresh()
        if el.name == 'exitButton':
            el.onMouseEnter = onExit
        if el.name == 'exitButtonGlow':
            el.opacity = 0
            el.onDraw = onExitGlowDraw

    # Application logic
    irc = IRC(channel=irc_channel,network=irc_network)
    irc.msghandler = msghandler
    irc.reportStatus = onReportStatus
    irc.start()

    # eventloop
    canvas.eventloop()

#
# IRC logic
#
class IRC(threading.Thread):
    msghandler = None
    reportStatus = None
    def __init__(self,network='irc.freenode.net',port=6667,
                    channel='maemo',nick='pyIRC'):
        threading.Thread.__init__(self)
        self.network = network
        self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.irc.connect ( ( network, port ) )
        trash = self.irc.recv ( 4096 )
        self.irc.send ( 'NICK %s\r\n'%nick )
        self.irc.send ( 'USER %s %s %s :%s\r\n'%(nick,nick,nick,nick) )
        self.irc.send ( 'JOIN #%s\r\n'%channel )


    def run(self):
        global msglist
        global exit_sign
        first_msg = True
        if self.reportStatus:
            self.reportStatus('Connecting ...')
        while True:
            if exit_sign:
                return

            data = self.irc.recv ( 4096 )

            if data.find ( 'PING' ) != -1:
                self.irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )

            elif data.find ( 'PRIVMSG' ) != -1:

                if first_msg and self.reportStatus:
                    self.reportStatus(self.network)
                    first_msg = False

                nick = data.split ( '!' ) [ 0 ].replace ( ':', '' )
                message = ':'.join ( data.split ( ':' ) [ 2: ] )
                if self.msghandler:
                    self.msghandler(nick,message)

if __name__ == '__main__':
    main()
