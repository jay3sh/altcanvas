Inkface is SVG based GUI framework. You design the GUI in an SVG image editor (like Inkscape/Illustrator) and use inkface framework to wire your program logic with the elements of your SVG GUI. The benefits of this approach:
  * Rich GUIs of any colors and any shapes.
  * Replacing the GUI is as trivial as replacing the old SVG file with new one.
  * Designing new GUIs/themes is extremely easy given that it involves modifying the SVG file in a full-fledged Image editor. Unlike other theme making scenarios, there is no need to create tons of .png files and storing them in standard directory structure.

## Update ##

Latest release **v0.2.3** [download](http://code.google.com/p/altcanvas/downloads/list)

The early releases of Inkface (from 0.0.1 to 0.1.3) were experiments or of proof-of-concept
nature. From the lessons learnt, I went through redesigning all of the project and have spent past month in reimplementing the framework. For the reasons behind these decisions, check this [blog post](http://jyro.blogspot.com/2009/02/planning-inkface-v02.html)

The major highlights in v0.2 are as follows:

  * Complete reimplementation in python. No need for recompile for different architectures/toolchains.
  * A basic SVG parser has been written from scratch in python. So no more dependencies on librsvg/libaltsvg. It is available as **inkface.altsvg** module
  * For actual rendering **pycairo** is used
  * For the canvas backend **pygame** is chosen. pygame gives mature interface to draw on X11 surfaces, so inventing one's own is unnecessary. The classes in **inkface.canvas** module, provide abstractions that are based on pygame. Pygame is well supported on Maemo platform, so maemo developers using inkface GUI will be more familiar with this new environment.

## Installation ##

  * Download source code:
    * Check out
> > > ` svn checkout http://altcanvas.googlecode.com/svn/trunk/inkface2/ inkface2 `
    * Tarball - Check the downloads for inkface-pygame-`<version>`-.tar.gz packages

  * Install

> > ` python setup.py install `

## Getting started ##

> `[`Note: The term "widget" used in traditional GUI toolkits is loosely synonymous with "SVG element" as used in following discussion`]`

### Composing the GUI ###
> Composing the GUI is no different than designing an image in a SVG image editor like Inkscape. The only thing one will have to do in addition to normal drawing, is **naming the SVG elements**. The programmer can later use these names to load these elements as widgets in his/her GUI at runtime. To name a SVG element all one has to do is, right-click on it and in the "Object Properties" dialog fill the **label** field with the desired name. The GUI designer has no need to know about any programming language.

### Coding for the GUI ###
  * Loading the GUI
> In order to simply load and display the GUI one has to write only 4 lines of pure python code. Check out [basic.py](http://code.google.com/p/altcanvas/source/browse/trunk/inkface-pygame/tests/basic.py?spec=svn952&r=952). This program takes SVG file name as command line input and loads it as GUI.
```
# Load the SVG file in a "Face" object
face = PygameFace(sys.argv[1])

# Create the backend canvas object of suitable size
canvas = PygameCanvas((int(face.svg.width),int(face.svg.height)))

# Add the face object to canvas
canvas.add(face)

# Call the infinite event handling loop
canvas.eventloop()
```

  * Adding event handlers
> The named elements from the SVG files will be accessible as attributes of the "face" objects. For example, if you drew a picture of a door and labeled it "quitButton", then you can access it as `face.quitButton`. If you want the program to exit upon left click of that door, then you can assign your exit routine as event handler of this quitButton
```
face.quitButton.onLeftClick = self.cleanupAndExit
...
def cleanupAndExit(self):
    sys.exit(0)
```

## Demo Videos ##
  * Based on v0.2
    * [Inkface pygame twitter client](http://blip.tv/file/1813720)
    * [smooth scrolling](http://blip.tv/file/1801444)

  * Based on v0.1.x
    * [Clutter Animation paths using Inkface](http://blip.tv/file/1747382)
    * [Clutter with Inkface](http://blip.tv/file/1658852)
    * [twitter client using inkface v0.1.2](http://blip.tv/file/1654627)
    * [Inkface v0.1 demo](http://blip.tv/file/1355876)
    * [How Inkface based GUI design works](http://blip.tv/file/1299872)


## Links ##
  * [Mailing list/Forum](http://groups.google.com/group/inkface)

  * Check out the issue tracker for features and bugs
    * [Features](http://code.google.com/p/altcanvas/issues/list?can=2&q=Type-Enhancement&colspec=ID+Summary+Status+Priority+Component&cells=tiles)
    * [Bugs](http://code.google.com/p/altcanvas/issues/list?can=2&q=Type-Defect&colspec=ID+Summary+Status+Priority+Component&cells=tiles)