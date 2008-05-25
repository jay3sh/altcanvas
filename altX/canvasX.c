#include <Python.h>
#include <stdio.h>

#include <X11/Xlib.h>

#include <cairo.h>

#include <pycairo.h>


#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d << %s >>\n", \
                __FILE__,__LINE__,__FUNCTION__); \
           exit(1); \
        }

#define PRINT_MARK \
        printf("%s:%d <<%s>>\n",__FILE__,__LINE__,__FUNCTION__);

static Pycairo_CAPI_t *Pycairo_CAPI;

static Window win,rwin;
static Display *dpy=NULL;
static int screen=0;
static int w=800;
static int h=480;
static int X=0;
static int Y=0;
static Pixmap pix;
static XGCValues gcv;
static GC gc;

static cairo_surface_t *xsurface;
static cairo_t *xctx;

static PyObject *canvas_run(PyObject *self,PyObject *pArgs)
{
    dpy = XOpenDisplay(0);
    ASSERT(dpy);

    rwin = DefaultRootWindow(dpy);
    ASSERT(rwin);

    screen = DefaultScreen(dpy);
    ASSERT(screen >= 0);

    win = XCreateSimpleWindow(
                dpy,
                rwin,
                X, Y,
                w, h,
                0,
                BlackPixel(dpy,screen),
                BlackPixel(dpy,screen));
    ASSERT(win);

    XMapWindow(dpy, win);

    pix = XCreatePixmap(dpy,
                        win,
                        w,h,
                        DefaultDepth(dpy,screen));
    ASSERT(pix);

    /*
     * Wait for first MapNotify to draw the initial window
     */
    XSelectInput(dpy, win, StructureNotifyMask);
    while(1)
    {
        XEvent event;
        XNextEvent(dpy,&event);
        if(event.type == MapNotify){
            break;
        }
    }

    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    XClearWindow(dpy, win);


    xsurface = cairo_xlib_surface_create(dpy, win, visual, w,h);
    ASSERT(xsurface);
    xctx = cairo_create(xsurface);
    ASSERT(xctx);


    //sleep(2);

    //XCloseDisplay(dpy);

    /*
     * Return None
     */
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_draw(PyObject *self,PyObject *pArgs)
{
    PyObject *obj = NULL;
    PycairoSurface *pysurface = NULL;
    cairo_surface_t *surface = NULL;
    if(PyArg_ParseTuple(pArgs,"O!",&PycairoSurface_Type,&obj)){
        ASSERT(obj);
        pysurface = (PycairoSurface *)obj;
        surface = pysurface->surface;
        ASSERT(surface);
        ASSERT(cairo_surface_status(surface) == CAIRO_STATUS_SUCCESS);
        cairo_set_source_surface(xctx,surface,100,100);
        //cairo_rectangle(xctx,3,3,5,5);
        cairo_paint(xctx);
        //cairo_fill(xctx);
        XFlush(dpy);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef canvas_methods[] =
{
    { "run",canvas_run,METH_VARARGS,NULL},
    { "draw",canvas_draw,METH_VARARGS,NULL},
    { NULL, NULL, 0, NULL }
};

DL_EXPORT(void)
initcanvasX(void)
{
    Pycairo_IMPORT;

    Py_InitModule("canvasX", canvas_methods);
}
