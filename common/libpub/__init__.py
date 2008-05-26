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
filename_list = None
CONFIG_FILE = ''

SERVER = 'http://www.altcanvas.com/xmlrpc/'
VERSION = '0.6.1'
HOSTAPP = '_'
SERVICE_CHOICE = '_'

IMAGE_DIR = '/home/jayesh/trunk/altcanvas/install'
#IMAGE_DIR = '/usr/share/altpublishr/icons'
    
def start(hostapp='_',fnames=None,guiwindow=None):
    global conf,window,filename_list,HOSTAPP
    
    HOSTAPP = hostapp
    
    filename_list = fnames
        
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
    
def start_prime():
    global conf,HOSTAPP,VERSION,IMAGE_DIR
    HOSTAPP = 'Maemo' 
    VERSION = '0.6.0'
    import utils.config
    conf = utils.config.Config()

    
        
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
    if SERVICE_CHOICE == 'FLICKR':
        conf.set('FLICKR_TOKEN',None)
    elif SERVICE_CHOICE == 'PICASAWEB':
        conf.set('PICASA_LAST_USERNAME',None)
        conf.set('PICASA_LAST_PASSWORD',None)
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
    
firefox_xpm = [
"48 48 248 2",
"  	c None",
". 	c #7980B8",
"+ 	c #5269AA",
"@ 	c #133988",
"# 	c #155AA7",
"$ 	c #1181BC",
"% 	c #13508E",
"& 	c #2773AF",
"* 	c #6976B1",
"= 	c #146CAB",
"- 	c #1785C4",
"; 	c #35A7E4",
"> 	c #5988A8",
", 	c #1A639C",
"' 	c #618380",
") 	c #7F896D",
"! 	c #576768",
"~ 	c #414E6D",
"{ 	c #2882BB",
"] 	c #36A2DD",
"^ 	c #41AEE7",
"/ 	c #2D8FCF",
"( 	c #2A4D6F",
"_ 	c #DDC563",
": 	c #FDFA57",
"< 	c #F7CC2C",
"[ 	c #D0A634",
"} 	c #EEB88A",
"| 	c #E86918",
"1 	c #40A3DD",
"2 	c #296599",
"3 	c #23568D",
"4 	c #164778",
"5 	c #16395A",
"6 	c #072558",
"7 	c #2C3B4D",
"8 	c #9D8D2F",
"9 	c #F8D801",
"0 	c #FAE800",
"a 	c #F6B704",
"b 	c #FBD46D",
"c 	c #A5A5C9",
"d 	c #062C70",
"e 	c #061646",
"f 	c #0A2E62",
"g 	c #123D74",
"h 	c #6D6D6C",
"i 	c #A99269",
"j 	c #EDB16B",
"k 	c #BABCA3",
"l 	c #907241",
"m 	c #B27A1C",
"n 	c #F69B08",
"o 	c #F6A706",
"p 	c #F7A613",
"q 	c #E15707",
"r 	c #E58836",
"s 	c #AE99A3",
"t 	c #111A54",
"u 	c #05122B",
"v 	c #061538",
"w 	c #142646",
"x 	c #17334F",
"y 	c #4F4B50",
"z 	c #D28D3D",
"A 	c #F0AC4C",
"B 	c #756D57",
"C 	c #CEA753",
"D 	c #FDE55B",
"E 	c #FEFA7A",
"F 	c #F9E641",
"G 	c #F9C617",
"H 	c #FCD9A3",
"I 	c #E98B66",
"J 	c #D64804",
"K 	c #E17B25",
"L 	c #D86A27",
"M 	c #685049",
"N 	c #795B48",
"O 	c #635B5B",
"P 	c #E48529",
"Q 	c #E99737",
"R 	c #B8832E",
"S 	c #214357",
"T 	c #45402F",
"U 	c #CB8F1C",
"V 	c #FCF604",
"W 	c #F7C603",
"X 	c #FBE5B6",
"Y 	c #E36743",
"Z 	c #D63003",
"` 	c #E99C4C",
" .	c #E17919",
"..	c #172B5B",
"+.	c #202A74",
"@.	c #0D223C",
"#.	c #7F5A1C",
"$.	c #FDE56F",
"%.	c #D15D41",
"&.	c #B83404",
"*.	c #D9782A",
"=.	c #E27A06",
"-.	c #277BC4",
";.	c #624B23",
">.	c #FBD659",
",.	c #F1E084",
"'.	c #DE7317",
").	c #E99725",
"!.	c #F6B12B",
"~.	c #EEA716",
"{.	c #EB9515",
"].	c #E68714",
"^.	c #CC590A",
"/.	c #192963",
"(.	c #66572F",
"_.	c #E9A603",
":.	c #AC320A",
"<.	c #8D564E",
"[.	c #4F6E8B",
"}.	c #4A9DC9",
"|.	c #FEFE92",
"1.	c #D95708",
"2.	c #4D2B18",
"3.	c #E79209",
"4.	c #FEFA86",
"5.	c #FDE6A6",
"6.	c #E6880C",
"7.	c #DA6917",
"8.	c #A4853C",
"9.	c #D47350",
"0.	c #CAAE8C",
"a.	c #D1B76B",
"b.	c #FCE424",
"c.	c #F08F0D",
"d.	c #FBEA3A",
"e.	c #0B345A",
"f.	c #836735",
"g.	c #AB8B53",
"h.	c #FEFD25",
"i.	c #B9571B",
"j.	c #C15822",
"k.	c #B66F38",
"l.	c #971703",
"m.	c #532725",
"n.	c #C09123",
"o.	c #FEFD39",
"p.	c #F9B517",
"q.	c #FAC94B",
"r.	c #A52504",
"s.	c #38313D",
"t.	c #9A8854",
"u.	c #FEFC17",
"v.	c #F9CA59",
"w.	c #D35B23",
"x.	c #B92707",
"y.	c #113A6F",
"z.	c #CC4621",
"A.	c #BE4910",
"B.	c #CD9750",
"C.	c #C12A11",
"D.	c #C8470A",
"E.	c #C63605",
"F.	c #A46F48",
"G.	c #C97A36",
"H.	c #89978D",
"I.	c #0F3C75",
"J.	c #A70209",
"K.	c #D35615",
"L.	c #E0650A",
"M.	c #BC7036",
"N.	c #0E3468",
"O.	c #9A1124",
"P.	c #25317F",
"Q.	c #FCDB47",
"R.	c #9B4967",
"S.	c #D77707",
"T.	c #CE5D15",
"U.	c #A84515",
"V.	c #342222",
"W.	c #0A2543",
"X.	c #A57736",
"Y.	c #F9D515",
"Z.	c #662817",
"`.	c #040B26",
" +	c #A06E32",
".+	c #C19471",
"++	c #970314",
"@+	c #D04911",
"#+	c #7E240E",
"$+	c #2D212E",
"%+	c #020935",
"&+	c #6C4538",
"*+	c #875F39",
"=+	c #FFFE6A",
"-+	c #883F67",
";+	c #291B1D",
">+	c #00071F",
",+	c #5C393C",
"'+	c #FEF2AE",
")+	c #FEFD4E",
"!+	c #CC9438",
"~+	c #B50501",
"{+	c #8B4B22",
"]+	c #7D4224",
"^+	c #FFFFC6",
"/+	c #BF9E8E",
"(+	c #762C5A",
"_+	c #C93B10",
":+	c #8B4E30",
"<+	c #543C54",
"[+	c #C66823",
"}+	c #D29A1D",
"|+	c #8E041A",
"1+	c #BC652C",
"2+	c #AE5B2C",
"3+	c #AF9393",
"4+	c #6E447E",
"5+	c #C11E00",
"6+	c #C32907",
"7+	c #FAE217",
"8+	c #650E41",
"9+	c #DF7931",
"0+	c #D86407",
"a+	c #7B0727",
"b+	c #DE9005",
"c+	c #DC8505",
"d+	c #EAB402",
"e+	c #EDC602",
"f+	c #A0776B",
"g+	c #B9140C",
"h+	c #C94617",
"i+	c #D04F22",
"j+	c #9C706E",
"k+	c #91697A",
"l+	c #850520",
"m+	c #79495B",
"n+	c #551D5F",
"o+	c #655191",
"p+	c #560D43",
"q+	c #81142A",
"r+	c #A81615",
"s+	c #A8371E",
"t+	c #8D362F",
"u+	c #632C4A",
"v+	c #563D7B",
"w+	c #453786",
"x+	c #471552",
"y+	c #3C185B",
"                                                                                                ",
"                                                                                                ",
"                                    . + @ # # $ # % @ & *                                       ",
"                              + @ = $ $ $ - ; ; $ = = = = = @ >                                 ",
"                          + = $ $ $ $ $ $ ; ; ; - = # # , ' ) ! ~ ~                             ",
"                      + % = = = = & & & { ] ^ ^ ; / = , % ( ! ) _ : < [ }                       ",
"          |         @ % % % % , , , , & & 1 ^ ^ ^ / & 2 3 4 5 6 6 7 8 9 0 a b                   ",
"        | | }   c d 6 e f g 4 4 h i j k & / ^ ^ ^ ^ { & 2 3 ( l m m n n o a a p                 ",
"        q | r s t e u v w x y z A A i ( 3 / ^ ^ ^ 1 { & & & 2 ~ B C D E F G o n n   H           ",
"      I J | K L M N y x 7 O P Q Q R x S & 1 ^ ^ { { & & & { 2 3 ( 5 T U < V V W n p X b         ",
"      Y Z J K j j j j j b `  .K Q y ..+./ ^ / & & { & { / ^ 1 & ( 5 w @.#.o 9 9 9 o A $.        ",
"      %.&.*.j A j A A Q Q K =. . .4 & -.] ^ -.-.& / ; ^ ^ ^ ^ / 3 3 ( ..w ;.n W W a n >.,.      ",
"      %.'.` ` A ).!.~.{.].=.=.'.^.y -.-.1 ^ ^ ] / ; ; ; ; ^ ^ 1 & 2 3 ( /.w (.n a _.o !.$.      ",
"      *.Q Q Q ~.~.{.{.].]. .'.'.^.:.<.[.> }.}.; ; ; ; ; ; ; ; ^ ^ { 3 { 2 3 S m n _.n !.|.X     ",
"    } P Q ~.{.{.{.].{.].]. . .'.1.:.J 1.q q 2.{ ] ; ; ; / ; ; ; ; 1 ] 1 1 { 2 S 3.n 3.n 4.5.    ",
"    Q ).).{.{.6.].].].K ]. .'.7.7.&.1.J q K i / ] ; ; ; ; ] / ] ] ] ] ] ] / & 8.m n !.o : $.    ",
"    Q ).].3.].].].].]. . .K '.K K 9.X X } 0.[.$ ] ] / ] ] { = , { / / / / / $ a.[ n $.a V b.    ",
"  j Q {.{.3.c.].].].]. . .'.| K K ` } j h 5 % - ; / $ { / / , , , { / / / / & i E c.$.d.0 9     ",
"  Q ).].3.].].].].K  . .'. .K K Q r I 7 e.% = / / - # , = { , , , , / / / -.3 f.E < $.D 9 W b   ",
"j Q ).].{.].].].].]. . .'.K P Q Q A g.f @ = / / ; / = , & , , , , , & / -., @ f.h.G $.4.9 W !.  ",
"` r ].{.{.6.].].].K  .'. .P r Q ` A C @ # = - / / / = , , , , , , % { / { # % l 0 9 4.|.G a !.  ",
"` ).].3.].6.].c. . . .K L i.j.j.k.C b % # $ -./ / / -., , , , , 3 % , { = , & R 9 W E |.< o !.  ",
"j P ].3.].6.].K  . .7.:.l.l.l.m.@.@.( @ # = -./ / / / / & , , 3 % % % % 4 ! & n.W G o.: p.n q.  ",
"j K ].c.6.]. . . .'.r.l.l.l.r.s.f f f @ # = -.-./ -./ / 3 , , 3 % % % % 4 a.t.o o W V u.p.!.v.  ",
"9.w.=.].]. . . . .7.l.l.r.r.x.N 4 @ @ # & -.-.-.-.{ -./ % 3 % % % @ % 4 y.C q.n n 9 0 V a >._   ",
"9.z.'. .K  . .'.7.A.r.r.x.&.&. .O # # 2 & -.-.-.-.-.-.{ & % % 4 % 4 4 @ 4 B.E n n 9 9 0 p 4.j   ",
"  C.'.'. .K '.'.K D.:.&.&.E.E.7. .F.2 # # 2 h G.r A a.H.{ % 4 4 I.4 I.I., B.|.!.o W 9 9 q.|.j   ",
"  J.7. .'.'.'.'.'.K.E.E.D.J J L.'.K 7.M.M.'.K '.K r A ,.H.4 4 y.N.y.N.N.3 [ |.q.a a W G 4.$.    ",
"  O.K.'.'.L. .'.K '.D.Z J J q q '.'.K 7.'.'. . . .7.7.j g.I.y.f f 6 6 P.3 !.E Q.o < a >.|.>.    ",
"  R.z.w.'.S.'.'.'.| 7.q q q q q &.A.7.'.K '.L T.A.U.V.u W.e.N.6 t e w X.O Y.h.G n v.p.4.|.C     ",
"    x.L L.'.'.'.'. .7. .q q L.q K.l.l.l.r.r.:.:.Z.`.`.u e t t e e e  + + +9 V W n b D 4.4..+    ",
"    ++L @+'.'.S.'. .'.'.'.L.L.L.L.D.l.l.r.#+Z.$+@.u %+v e e e %+e &+6.*+n 9 9 a q.4.: =+Q.      ",
"    -+z.E. .'.'.S.L.'. .L. .7.'.L. .i.;+>+>+u w /.%+%+e e %+%+%+,+ .].c.a W W o '+)+o.)+!+      ",
"      J.~+7.'.'.'.'.'.'.S.L. .L.'. .7. .{+v %+/.t %+%+%+%+%+%+]+| L  .c._._._.v.^+V u.b./+      ",
"      (+~+_+K 1.'.'. .'.'.S.'.'.S.L. .'.'.'.:+<+P.+.t %+%+m.[+'.'.'.'.6.3.3.~.|.4.V V }+        ",
"        |+~+@+7.7.'.K '.'.'.'.'.'.S.=.L.'.'.'.'.'.1+2+[+ . .'.'. . .'.=.=.=.d.E d.0 9 3+        ",
"        4+~+5+K.6+7.K P 7. .'.'.'.'.'.'.'.'.'.'. .'.'.7.K 7.K 7. .7.L.L.S.7+o.: 9 9 R           ",
"          8+~+5+J 5+K.9+K C.1.'. . .'.'.L.'. .K K P r r r r r K 7.q 0+S.9 V h.Y.9 _.            ",
"            a+~+6+Z ~+6+r 9+~+E.7.K K 7.K. .'.K K K K K K '.'.'.0+0+b+9 0 V V W a 3+            ",
"              ++~+E.6+~+~+z.r C.~+_+w.P 9+K.@+K.7.'.'. . .'.7.0+c+_.d+e+0 0 e+_.f+              ",
"                ++~+6+5+~+~+g+z.g+g+g+C.h+%.r L i+@+@+T.T.0+S.c+b+_.d+e+e+e+3.j+                ",
"                  a+~+~+~+~+~+~+g+g+g+g+g+g+g+_+h+w._+D.^.^.0+S.c+b+d+d+_.'.k+                  ",
"                    8+J.~+~+~+~+g+g+g+g+g+g+g+g+C.6+&.D.D.^.0+S.S.b+3.].2+                      ",
"                        l+~+~+~+g+~+g+g+g+g+g+g+C.C.6+_+D.D.^.0+S.S.[+m+                        ",
"                          n+a+~+g+g+g+g+g+g+g+g+g+C.6+E._+D.^.0+2+m+                            ",
"                              o+p+q+r+g+g+g+g+g+g+x.C.E.s+t+u+v+                                ",
"                                      w+x+x+x+x+x+x+y+w+                                        ",
"                                                                                                "
]    
    
