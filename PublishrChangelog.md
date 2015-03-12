# Publishr changelog #

[Track existing issues and add new ones](http://code.google.com/p/altcanvas/issues/list)

**Plans for next version**
  * Improved GUI for multiple image upload for Maemo.

**Changelog for 0.5**
  * Generic changes
    1. Image preview
    1. Choice for remembering the service (Flickr/Picasa). Allowing faster progress through upload process for general case.
    1. Choice for remembering Picasaweb password (stored with a weak cipher). Further speeding through upload process for general case.
    1. Improvement in exception handling
    1. Use of gdkpixbuf instead of imagemagick. This allows **Inkscape plugin to work on Windows** too. (Thanks to Andrea for the patch) (I couldn't find extensions directory on windows, so couldn't test it, please report if you do)
    1. Button to open final upload links in Firefox (_works on Linux only_) and Maemo browser.

  * Maemo specific changes
    1. Option to upload multiple jpeg/gif images in a single directory.

**Changelog for 0.3.2**
  1. Fixed failures for some corner cases.
  1. Tested that it works for Gimp >= 2.0 and Python >= 2.4

**Changelog for 0.3.1**

Thanks to some early users, one mistake got uncovered that was resulting in unnecessary crash. Fixed it and put new package as 0.3.1.

**Changelog for 0.3**

  1. Support for photosets (flickr) and albums (picasaweb). You can choose from existing ones or create new.
  1. Crash report dialog that will help you report crashes in corner cases. Most importantly the mysterious absence of "Publish to web" in menu for some users, will have an explanation.
  1. Improved UI that remembers your last choices wherever it can
  1. Uses latest release of gdata API (1.0.10.1) that has in-built support for picasaweb
  1. More compact organization of files (only two entries in plugin directory - publishr.py, libpub) Installation procedure remains the same, but you might want to delete old files from plugins directory.