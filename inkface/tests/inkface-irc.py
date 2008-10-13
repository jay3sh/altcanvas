#!/usr/bin/env python

import os
import sys
import inkface
import socket
import threading

canvas = None

DATA_DIR='tests/data'
KEYBOARD_SVG='keyboard-layout.svg'
IRC_SVG='irc.svg'

msglist = []
msgtxtlist = [None,None,None,None,None]

def msghandler(nick,msg):
    global msgtxtlist
    global msglist
    
    print msg
    clean_msg = nick+': '+msg.strip()
    '''
    if(len(clean_msg) > 50):
        final_msg = clean_msg[:50]+'...'
    else:
        final_msg = clean_msg
    '''
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

def onMsgboxDraw(elem):
    global canvas
    i = int(elem.name[6])
    if(i == 0 or i < len(msglist)):
        canvas.draw(elem)

def main():
    global canvas
    global msgtxtlist

    irc_network = 'irc.freenode.net'
    irc_channel = 'ubuntu'

    irc = IRC(channel=irc_channel,network=irc_network)
    irc.msghandler = msghandler
    irc.start()

    elements = inkface.loadsvg(os.path.join(DATA_DIR,IRC_SVG))
    canvas = inkface.canvas()
    canvas.register_elements(elements)

    for el in elements:
        if el.name.startswith('msgtxt'):
            i = int(el.name[6])
            msgtxtlist[i] = el
            el.text = ''
            el.refresh()

        if el.name.startswith('msgbox'):
            el.onDraw = onMsgboxDraw

        if el.name == 'networkName':
            el.text = irc_network
            el.refresh()
        if el.name == 'channelName':
            el.text = irc_channel
            el.refresh()

    canvas.show()
    canvas.eventloop()


class IRC(threading.Thread):
    msghandler = None
    def __init__(self,network='irc.freenode.net',port=6667,
                    channel='maemo',nick='pyIRC'):
        threading.Thread.__init__(self)
        self.irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
        self.irc.connect ( ( network, port ) )
        trash = self.irc.recv ( 4096 )
        self.irc.send ( 'NICK %s\r\n'%nick )
        self.irc.send ( 'USER %s %s %s :%s\r\n'%(nick,nick,nick,nick) )
        self.irc.send ( 'JOIN #%s\r\n'%channel )

    def run(self):
        global msglist
        while True:
            data = self.irc.recv ( 4096 )
            if data.find ( 'PING' ) != -1:
                self.irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
            elif data.find ( 'PRIVMSG' ) != -1:
                nick = data.split ( '!' ) [ 0 ].replace ( ':', '' )
                message = ':'.join ( data.split ( ':' ) [ 2: ] )
                if self.msghandler:
                    self.msghandler(nick,message)

if __name__ == '__main__':
    main()
