#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.59)
AC_INIT(libxpy, 0.1, jayesh@altfrequency.com)
AC_CONFIG_SRCDIR([altX.c])
AC_CONFIG_HEADER([config.h])

AM_INIT_AUTOMAKE([1.8 foreign])

# Checks for programs.
AC_PROG_CC

# Checks for libraries.
AC_PROG_LIBTOOL

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

AC_CONFIG_FILES([Makefile])

AM_PATH_PYTHON(2.5) 

# cairo                                                                       
PKG_CHECK_MODULES(CAIRO, cairo >= 1.4)                     
if test -n "$export_dynamic"; then                                            
    CAIRO_LIBS=`echo $CAIRO_LIBS | sed -e "s/$export_dynamic//"`                
fi                                                                            

#pycairo
PKG_CHECK_MODULES(PYCAIRO, pycairo >= 1.4)                     
if test -n "$export_dynamic"; then                                            
    PYCAIRO_LIBS=`echo $PYCAIRO_LIBS | sed -e "s/$export_dynamic//"`                
fi                                                                            

#GTK
PKG_CHECK_MODULES(GTK, gtk+-2.0 >= 2.0)
if test -n "$export_dynamic"; then
    GTK_LIBS=`echo $GTK_LIBS | sed -e "s/$export_dynamic//"`
fi

#GThread
PKG_CHECK_MODULES(GTHREAD, gthread-2.0 >= 2.0)
if test -n "$export_dynamic"; then
    GTHREAD_LIBS=`echo $GTHREAD_LIBS | sed -e "s/$export_dynamic//"`
fi

#X11
PKG_CHECK_MODULES(X11, x11 >= 1.1)
if test -n "$export_dynamic"; then
    X11_LIBS=`echo $X11_LIBS | sed -e "s/$export_dynamic//"`
fi


# Checks for header files ---
AM_CHECK_PYTHON_HEADERS(,[AC_MSG_ERROR(could not find Python headers)])


# Checks for library functions.
AC_OUTPUT
