#!/usr/bin/env python

import sys
import pygst
pygst.require("0.10")
import gst
import gtk

def main():
    player = gst.element_factory_make("playbin", "player")
    player.set_property('uri', "file://" + sys.argv[1])
    player.set_state(gst.STATE_PLAYING)

    '''
    control = gst.Controller(player, "volume")
    control.set_interpolation_mode("volume", gst.INTERPOLATE_LINEAR)

    control.set("volume", 0, 0.0)
    control.set("volume", 2 * gst.SECOND, 1.0)
    control.set("volume", 4 * gst.SECOND, 0.0)
    control.set("volume", 6 * gst.SECOND, 1.0)
    control.set("volume", 8 * gst.SECOND, 0.0)
    control.set("volume", 10 * gst.SECOND, 1.0)
    '''

    gtk.main()

if __name__ == "__main__":
    main()
