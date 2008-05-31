#include <Python.h>

#include <stdio.h>
#include <cairo.h>
#include <cairo-xlib.h>

#include <pycairo.h>

/*
 * MACRO definitions
 */

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d\n",__FILE__,__LINE__); \
           exit(1); \
        }
#define PycairoAltXSurface PycairoSurface

#define TRACE_ENTRY \
    printf("Entering %s\n",__FUNCTION__);
#define TRACE_EXIT \
    printf("Exiting %s\n",__FUNCTION__);

/*
 * Static variables
 */
static Pycairo_CAPI_t *Pycairo_CAPI;
static Display *dpy=NULL;
static GC gc=NULL;

/*
 * Private helper function declarations
 */
cairo_surface_t *create_altx_surface();

PyObject *
Alt_PycairoSurface_FromSurface (cairo_surface_t *surface, PyObject *base);


/*
 * Module method definitions
 */
static PyObject *
altx_surface_new (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    TRACE_ENTRY
    PyObject *obj;
    cairo_surface_t *surface;

    
    surface = create_altx_surface();

    //Py_INCREF((PyObject *)dpy);
    //Py_INCREF((PyObject *)gc);

    return Alt_PycairoSurface_FromSurface(surface,NULL);
}

static PyObject *
altx_surface_close(PycairoAltXSurface *o)
{
    TRACE_ENTRY
    //Py_DECREF((PyObject *)dpy);
    //Py_DECREF((PyObject *)gc);
    XCloseDisplay(dpy);
}

static PyObject *
altx_surface_flush(PycairoAltXSurface *o)
{
    TRACE_ENTRY
    //printf("dpy = %p, gc = %p\n",dpy,gc);

    //XDrawLine(dpy, win, gc, 30, 80, 180, 20);
    XFlush(dpy);
}

static PyMethodDef altx_surface_methods[] = {
    {"close", (PyCFunction)altx_surface_close,    METH_NOARGS },
    {"flush", (PyCFunction)altx_surface_flush,    METH_NOARGS },
    {NULL, NULL, 0, NULL},
};

PyTypeObject PycairoAltXSurface_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "altX.AltXSurface",                /* tp_name */
    sizeof(PycairoAltXSurface),         /* tp_basicsize */
    0,                                  /* tp_itemsize */
    0,                                  /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    altx_surface_methods,               /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0, /* &PycairoSurface_Type, */      /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)altx_surface_new,          /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};





static PyMethodDef xpy_methods[] =
{
    {NULL,NULL,0,NULL}
};



DL_EXPORT(void)
initaltX(void)
{
    TRACE_ENTRY
    PyObject *m;

    Pycairo_IMPORT;

    /*
    PycairoSurface_Type.tp_base = &PyBaseObject_Type;
    if (PyType_Ready(&PycairoSurface_Type) < 0)
        return;
    */

    PycairoAltXSurface_Type.tp_base = &PycairoSurface_Type;
    if (PyType_Ready(&PycairoAltXSurface_Type) < 0)
        return;

    m = Py_InitModule("altX", xpy_methods);

    Py_INCREF(&PycairoAltXSurface_Type);

    PyModule_AddObject(m, "AltXSurface",
        (PyObject *)&PycairoAltXSurface_Type);

}

PyObject *
Alt_PycairoSurface_FromSurface (cairo_surface_t *surface, PyObject *base)
{
    TRACE_ENTRY
    PyTypeObject *type = NULL;
    PyObject *o;

    ASSERT(surface != NULL);

    if (Pycairo_Check_Status(cairo_surface_status(surface))) {
	    cairo_surface_destroy (surface);
	    return NULL;
    }

    type = &PycairoAltXSurface_Type;

    o = type->tp_alloc (type, 0);

    if (o == NULL) {
	    cairo_surface_destroy (surface);
    } else {
	    ((PycairoSurface *)o)->surface = surface;
	    Py_XINCREF(base);
	    ((PycairoSurface *)o)->base = base;
    }
    return o;
}

cairo_surface_t *
create_altx_surface()
{
    TRACE_ENTRY
    Window win,rwin;
    int screen = 0;
    int w=100, h=100;
    int x=0, y=0;
    Pixmap pix;
    XGCValues gcv;


    ASSERT(dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(dpy));
    screen = DefaultScreen(dpy);

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    x, y,
                    w, h,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    XMapWindow(dpy, win);

    ASSERT(pix = XCreatePixmap(dpy,
                            win,
                            w,h,
                            DefaultDepth(dpy,screen)));

    gcv.foreground = WhitePixel(dpy,screen);
    ASSERT(gc = XCreateGC(dpy,pix,GCForeground,&gcv));


    XSelectInput(dpy, win, StructureNotifyMask);

    while(1)
    {
        XEvent event;

        XNextEvent(dpy, &event);
        if (event.type == MapNotify)
            break;
    }


    XDrawLine(dpy, win, gc, 10, 60, 180, 20);
    //XFillRectangle(dpy, pix, gc, x, y, w, h);
    cairo_surface_t *surface;
    cairo_t *cr;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));

    //XClearWindow(dpy, win);
    surface = cairo_xlib_surface_create(dpy, win, visual, w,h);

    // EXTRA DEBUG STUFF
    XDrawLine(dpy, win, gc, 20, 70, 180, 20);
    XFlush(dpy); 
    // EXTRA DEBUG STUFF
    //

    //printf("dpy = %p, win = %p, gc = %p, pixmap = %x\n",
     //   dpy,win,gc,pix);
    
    return surface;

}

/*

int main(int argc, char *argv[])
{
    Window win,rwin;
    Display *dpy=NULL;
    int screen = 0;
    int w=100, h=100;
    int x=0, y=0;
    Pixmap pix;
    XGCValues gcv;
    GC gc;


    ASSERT(dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(dpy));
    screen = DefaultScreen(dpy);

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    x, y,
                    w, h,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    XMapWindow(dpy, win);

    ASSERT(pix = XCreatePixmap(dpy,
                            win,
                            w,h,
                            DefaultDepth(dpy,screen)));

    gcv.foreground = WhitePixel(dpy,screen);
    ASSERT(gc = XCreateGC(dpy,pix,GCForeground,&gcv));


    XSelectInput(dpy, win, StructureNotifyMask);


    while(1)
    {
        XEvent event;

        XNextEvent(dpy, &event);
        if (event.type == MapNotify)
            break;
    }

    printf("Filling!\n");

    //XDrawLine(dpy, win, gc, 10, 60, 180, 20);
    //XFillRectangle(dpy, pix, gc, x, y, w, h);
    /*
     * CAIRO Drawing
     * /
    cairo_surface_t *surface;
    cairo_t *cr;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));

    XClearWindow(dpy, win);
    surface = cairo_altx_surface_create(dpy, win, visual, w,h);
    cr = cairo_create(surface);

    cairo_set_source_rgb(cr, 0.8, 0.8, 0.8);

    #define SIZE 20
    cairo_move_to(cr, 20, 20);
    cairo_rel_line_to(cr,  2*SIZE,   0);
    cairo_rel_line_to(cr,   0,  2*SIZE);
    cairo_rel_line_to(cr, -2*SIZE,   0);
    cairo_close_path(cr);

    cairo_fill(cr);


    if (cairo_status (cr)) {
        printf("Cairo is unhappy: %s\n",
            cairo_status_to_string (cairo_status (cr)));
        exit(0);
    }

    cairo_destroy(cr);
    cairo_surface_destroy(surface);


    XFlush(dpy);

    sleep(10);

    printf("Done!\n");

    XCloseDisplay(dpy);

    return 0;
}
*/
