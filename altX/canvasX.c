#include <Python.h>
#include <stdio.h>

#include <X11/Xlib.h>

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d << %s >>\n", \
                __FILE__,__LINE__,__FUNCTION__); \
           exit(1); \
        }

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

    sleep(4);
    XCloseDisplay(dpy);
    /*
    surface = cairo_xlib_surface_create(dpy, win, visual, w,h);
    ASSERT(surface);
    ctx = cairo_create(surface);
    ASSERT(ctx);
    */

    /*
     * Return None
     */
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef canvas_methods[] =
{
    { "run",canvas_run,METH_VARARGS,NULL},
    { NULL, NULL, 0, NULL }
};

DL_EXPORT(void)
initcanvasX(void)
{
    Py_InitModule("canvasX", canvas_methods);
}
