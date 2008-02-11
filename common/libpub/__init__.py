#!/usr/bin/env python

# Publishr to publish images on web
# Copyright (C) 2007  Jayesh Salvi 
# http://www.altcanvas.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

'''publishr plugin library '''

import os
import sys
import gtk

window = None
conf = None
filename = '/tmp/test123.jpg'
CONFIG_FILE = ''

SERVER = 'http://www.altcanvas.com/xmlrpc/'
VERSION = '0.3.2'
HOSTAPP = '_'
    
def start(hostapp='_',fname='/tmp/test123.jpg',guiwindow=None):
    global conf,window,filename,HOSTAPP
    HOSTAPP = hostapp
    filename = fname
    import utils.config
    import control
    conf = utils.config.Config()
    if not guiwindow:
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    else:
        window = guiwindow
    window.connect("delete_event",delete_event)
    window.connect("destroy",destroy)
        
    _control = control.Control(window)
    _control.entry()
        
    window.show()
    
        
LicenseList = [
    (0,"All rights reserved",
         None),
    (4,"Attribution License",
         "http://creativecommons.org/licenses/by/2.0/"),
    (6,"Attribution-NoDerivs License",
         "http://creativecommons.org/licenses/by-nd/2.0/"),
    (3,"Attribution-NonCommercial-NoDerivs License",
         "http://creativecommons.org/licenses/by-nc-nd/2.0/"),
    (2,"Attribution-NonCommercial License",
         "http://creativecommons.org/licenses/by-nc/2.0/"),
    (1,"Attribution-NonCommercial-ShareAlike License",
         "http://creativecommons.org/licenses/by-nc-sa/2.0/"),
    (5,"Attribution-ShareAlike License",
         "http://creativecommons.org/licenses/by-sa/2.0/")
]
        
def alert(msg,type=gtk.MESSAGE_ERROR):
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()
    
def alert_markup(msg,type=gtk.MESSAGE_ERROR):
    msgDlg = gtk.MessageDialog(window,
                    gtk.DIALOG_DESTROY_WITH_PARENT|gtk.DIALOG_MODAL,
                    type,
                    gtk.BUTTONS_CLOSE,
                    '')
    msgDlg.set_markup(msg)
    msgDlg.connect("response", lambda dlg, resp: dlg.destroy())
    responseId = msgDlg.run()

def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()

def signout(widget=None,data=None):
    conf.set('FLICKR_TOKEN',None)
    # Quit the GUI
    destroy()
    
home_xpm = [
"16 16 65 1",
"  c black",
". c #0B0E09",
"X c #111111",
"o c gray8",
"O c #191919",
"+ c #3D1B14",
"@ c gray18",
"# c #273122",
"$ c #333D2F",
"% c #323232",
"& c #343434",
"* c #393939",
"= c #3F3F3F",
"- c #354031",
"; c #364530",
": c #431D15",
"> c #50231A",
", c #53251B",
"< c #57261D",
"1 c #612B20",
"2 c #763E2F",
"3 c #424A40",
"4 c gray29",
"5 c #465541",
"6 c #495545",
"7 c #5B5B5B",
"8 c #566252",
"9 c #586455",
"0 c #5B6657",
"q c #606060",
"w c #656565",
"e c gray40",
"r c #A54937",
"t c #A95849",
"y c gray52",
"u c #8B8B8B",
"i c #979797",
"p c #9B9B9B",
"a c #AAAAAA",
"s c #B4B4B4",
"d c gray71",
"f c #B6B6B6",
"g c #BBBBBB",
"h c #BCBCBC",
"j c gray77",
"k c gray79",
"l c #CACACA",
"z c gray80",
"x c #CECECE",
"c c gray81",
"v c #D2D2D2",
"b c LightGray",
"n c gray86",
"m c gainsboro",
"M c #DFDFDF",
"N c gray88",
"B c #E2E2E2",
"V c #E4E4E4",
"C c gray91",
"Z c #E9E9E9",
"A c #EAEAEA",
"S c gray93",
"D c #EFEFEF",
"F c gray100",
"G c None",
"GGGGGGGGGGGGGGGG",
"GGG   G  GGGGGGG",
"GGG t  w7 GGGGGG",
"GGG 2 7iAe GGGGG",
"GGG X*ulCjp GGGG",
"GGG 4pAjAlCy GGG",
"GG 4slAlClCxp GG",
"G O AlAxC@3& o G",
"GGG M><+D*F% GGG",
"GGG N,r,S@*@ GGG",
"GGG M,r,Vhmh GGG",
"GGG B,r<ndvs GGG",
"GGG n<<:xhbs GGG",
"G 33005;#.86-$6G",
"G3  66666 6666GG",
"GGGGGGGGGGGGGGGG"]
    
    
    
