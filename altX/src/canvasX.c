#include <Python.h>
#include <stdio.h>

#include <X11/X.h>
#include <X11/Xlib.h>
#include <X11/Xatom.h>

#include <cairo.h>

#include <pycairo.h>


#ifdef HAS_XSP
#include <X11/extensions/Xsp.h>

/* device specific data */
#define DEV_X_DELTA 3378
#define DEV_Y_DELTA 3080
#define DEV_X_CORRECTION -300
#define DEV_Y_CORRECTION -454

/**
   translate raw device coordinates to screen coordinates
*/
#define TRANSLATE_RAW_COORDS(x, y) \
{ \
  * x += DEV_X_CORRECTION;\
  * y += DEV_Y_CORRECTION;\
  * x = w - (w * *x) / DEV_X_DELTA;\
  * y = h - (h * *y) / DEV_Y_DELTA;\
}

static int xsp_event_base=-1;

#endif /* HAS_XSP */


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

static PyObject *motion_handler = NULL;
static PyObject *pressure_handler = NULL;

static PyObject *canvas_create(PyObject *self,PyObject *pArgs)
{
    int status = 0;
    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;

    dpy = XOpenDisplay(0);
    ASSERT(dpy);

    rwin = DefaultRootWindow(dpy);
    ASSERT(rwin);

    screen = DefaultScreen(dpy);
    ASSERT(screen >= 0);

    atoms_WINDOW_STATE
        = XInternAtom(dpy, "_NET_WM_STATE",False);
    ASSERT((atoms_WINDOW_STATE != BadAlloc && 
            atoms_WINDOW_STATE != BadValue));
    atoms_WINDOW_STATE_FULLSCREEN
        = XInternAtom(dpy, "_NET_WM_STATE_FULLSCREEN",False);
    ASSERT((atoms_WINDOW_STATE_FULLSCREEN != BadAlloc && 
            atoms_WINDOW_STATE_FULLSCREEN != BadValue));

    win = XCreateSimpleWindow(
                dpy,
                rwin,
                X, Y,
                w, h,
                0,
                BlackPixel(dpy,screen),
                BlackPixel(dpy,screen));
    ASSERT(win);

    /* Set the wmhints needed for fullscreen */
    status = XChangeProperty(dpy, win, atoms_WINDOW_STATE, XA_ATOM, 32,
                    PropModeReplace,
                    (unsigned char *) &atoms_WINDOW_STATE_FULLSCREEN, 1);
    ASSERT(status != BadAlloc);
    ASSERT(status != BadAtom);
    ASSERT(status != BadMatch);
    ASSERT(status != BadPixmap);
    ASSERT(status != BadValue);
    ASSERT(status != BadWindow);

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

#ifdef HAS_XSP
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;
    /* get xsp event base */
    XSPQueryExtension(dpy,
                    &xsp_event_base,
                    &xsp_error_base,
                    &xsp_major,
                    &xsp_minor);
    ASSERT(xsp_event_base >= 0);

    XSPSetTSRawMode(dpy, True);
#endif

    xsurface = cairo_xlib_surface_create(dpy, win, visual, w,h);
    ASSERT(xsurface);
    xctx = cairo_create(xsurface);
    ASSERT(xctx);


    /*
     * Return None
     */
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_run(PyObject *self,PyObject *pArgs)
{
#ifdef HAS_XSP
    int tx=0,ty=0,pressure=0;
    XSPRawTouchscreenEvent xsp_event;
#endif

    XSelectInput(dpy, win, 
        StructureNotifyMask | PointerMotionMask | ExposureMask);

    while(1)
    {
        XMotionEvent *mevent;
        XEvent event;

        XNextEvent(dpy, &event);
        switch(event.type){
        case MapNotify:
            break;
        case MotionNotify:
            mevent = (XMotionEvent *)(&event);
            if(motion_handler){ //TODO better check
                //PyEval_CallFunction(motion_handler,"ii",
                 //   mevent->x,mevent->y);
                PyEval_CallMethod(motion_handler,"motion_handler",
                                    "ii",mevent->x,mevent->y);
            }
            break;
        case KeyPress:
            exit(0);
            break;
        default:
            #ifdef HAS_XSP
            if(event.type == xsp_event_base){
                memcpy(&xsp_event, &event,
                    sizeof(XSPRawTouchscreenEvent));
                tx = xsp_event.x;
                ty = xsp_event.y;
                pressure = xsp_event.pressure;

                /* translate raw coordinates */
                TRANSLATE_RAW_COORDS(&tx, &ty);

                if(pressure_handler){
                    PyEval_CallFunction(pressure_handler,
                        "iii",tx,ty,pressure);
                }
            }
            #endif
            break;
        }
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_draw(PyObject *self,PyObject *pArgs)
{
    PyObject *obj = NULL;
    PycairoSurface *pysurface = NULL;
    int x=0,y=0;
    cairo_surface_t *surface = NULL;
    if(PyArg_ParseTuple(pArgs,"O!ii",&PycairoSurface_Type,&obj,&x,&y))
    {
        XClearWindow(dpy, win);
        ASSERT(obj);
        pysurface = (PycairoSurface *)obj;
        ASSERT(pysurface);
        surface = pysurface->surface;
        ASSERT(surface);
        ASSERT(cairo_surface_status(surface) == CAIRO_STATUS_SUCCESS);
        cairo_set_source_surface(xctx,surface,x,y);
        cairo_paint(xctx);
        XFlush(dpy);
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_close(PyObject *self,PyObject *pArgs)
{
    XCloseDisplay(dpy);
    
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_register_key_handler(
        PyObject *self,PyObject *pArgs)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_register_motion_handler(
        PyObject *self,PyObject *pArgs)
{
    PyObject *obj = NULL;

    if(PyArg_ParseTuple(pArgs,"O",&obj))
    {
        motion_handler = obj;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject *canvas_register_pressure_handler(
        PyObject *self,PyObject *pArgs)
{
    PyObject *obj = NULL;

    if(PyArg_ParseTuple(pArgs,"O",&obj))
    {
        pressure_handler = obj;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef canvas_methods[] =
{
    { "create",
        canvas_create,METH_VARARGS,NULL},
    { "run",
        canvas_run,METH_VARARGS,NULL},
    { "register_motion_handler",
        canvas_register_motion_handler,METH_VARARGS,NULL},
    { "register_pressure_handler",
        canvas_register_pressure_handler,METH_VARARGS,NULL},
    { "draw",
        canvas_draw,METH_VARARGS,NULL},
    { "close",
        canvas_close,METH_VARARGS,NULL},
    { NULL, NULL, 0, NULL }
};

DL_EXPORT(void)
initcanvasX(void)
{
    Pycairo_IMPORT;

    Py_InitModule("canvasX", canvas_methods);
}
