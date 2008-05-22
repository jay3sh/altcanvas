

bin_PROGRAMS	= animX animGdk

animX_LDADD	= $(CAIRO_LIBS)
animX_CPPFLAGS	= $(CAIRO_CFLAGS)
animX_SOURCES	= animX.c

animGdk_LDADD	= $(GTK_LIBS) $(GTHREAD_LIBS)
animGdk_CPPFLAGS= $(GTK_CFLAGS) $(GTHREAD_CFLAGS)
animGdk_SOURCES	= animGdk.c

lib_LTLIBRARIES     = altX.la canvasX.la

altX_la_LDFLAGS   = -module
altX_la_LIBADD	= $(CAIRO_LIBS) 
altX_la_CPPFLAGS	= $(PYTHON_INCLUDES) $(CAIRO_CFLAGS) $(PYCAIRO_CFLAGS)
#altX_la_CPPFLAGS	= -I/usr/local/include $(CAIRO_CFLAGS) $(PYCAIRO_CFLAGS)
altX_la_SOURCES   = altX.c


canvasX_la_CPPFLAGS = $(PYTHON_INCLUDES)
canvasX_la_LDFLAGS	= -module
canvasX_la_SOURCES	= canvasX.c
