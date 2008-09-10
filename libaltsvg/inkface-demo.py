#!/usr/bin/env python

import os
import gtk

IMAGE_BASE='/usr/share/pixmaps'
player_gui_images = {'Auditorium':IMAGE_BASE+'/music-player-auditorium.svg',
              'Sunset':IMAGE_BASE+'/music-player-sunset.svg'}

keyboard_gui_images = {'Playful':IMAGE_BASE+'/keyboard-playfull.svg',
                'Formal':IMAGE_BASE+'/keyboard-formal.svg',
                'Elegant':IMAGE_BASE+'/keyboard-elegant.svg'}

player_gui = None
keyboard_gui = None

def main():
    window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    window.connect("delete_event",delete_event)
    window.connect("destroy",destroy)

    vbox = gtk.VBox()

    keyboard_box = gtk.HBox()
    player_box = gtk.HBox()

    # Keyboard controls
    global keyboard_gui

    keyboard_label = gtk.Label('Keyboard')
    keyboard_launch = gtk.Button('Launch')
    keyboard_launch.connect("clicked",launch_keyboard)
    keyboard_gui = gtk.combo_box_entry_new_text()
    for title in keyboard_gui_images.keys():
        keyboard_gui.append_text(title)
    keyboard_gui.set_active(0)

    keyboard_box.pack_start(keyboard_label,expand=True)
    keyboard_box.pack_start(keyboard_gui,expand=True)
    keyboard_box.pack_start(keyboard_launch,expand=False)
    keyboard_box.set_spacing(10)
    keyboard_box.set_border_width(5)

    # Player controls
    global player_gui

    player_label = gtk.Label('Player')
    player_launch = gtk.Button('Launch')
    player_launch.connect("clicked",launch_player)
    player_gui = gtk.combo_box_entry_new_text()
    for title in player_gui_images.keys():
        player_gui.append_text(title)
    player_gui.set_active(0)

    player_box.pack_start(player_label,expand=True)
    player_box.pack_start(player_gui,expand=True)
    player_box.pack_start(player_launch,expand=False)
    player_box.set_spacing(10)
    player_box.set_border_width(5)

    vbox.pack_start(keyboard_box,expand=False)
    vbox.pack_start(player_box,expand=False)

    exitButton = gtk.Button('Exit')
    exitButton.connect("clicked",destroy)
    exitBox = gtk.HBox()
    exitBox.pack_start(gtk.Label(' '*20),expand=False)
    exitBox.pack_start(exitButton,expand=True)
    exitBox.pack_start(gtk.Label(' '*20),expand=False)
    vbox.pack_start(exitBox,expand=False)
    vbox.set_spacing(5)
    vbox.set_border_width(5)

    window.add(vbox)
    window.show_all()

    gtk.main()


def delete_event(widget,event,data=None):
    return False
    
def destroy(widget=None,data=None):
    gtk.main_quit()

def launch_player(widget,data=None):
    model = player_gui.get_model()
    active = player_gui.get_active()
    key = model[active][0]
    gui_filename = player_gui_images[key]
    os.environ['CENTER_COVER_ART'] = IMAGE_BASE+'/dido.png'
    os.environ['PREV_COVER_ART'] = IMAGE_BASE+'/corrs.png'
    os.environ['NEXT_COVER_ART'] = IMAGE_BASE+'/jem.png'
    (sin,soe) = os.popen4('/usr/bin/player '+gui_filename) 
    for l in soe:
        print l

def launch_keyboard(widget,data=None):
    model = keyboard_gui.get_model()
    active = keyboard_gui.get_active()
    key = model[active][0]
    gui_filename = keyboard_gui_images[key]
    (sin,soe) = os.popen4('/usr/bin/keyboard '+gui_filename) 
    for l in soe:
        print l

if __name__ == '__main__':
    main()
