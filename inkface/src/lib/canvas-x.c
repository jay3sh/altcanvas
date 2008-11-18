
#include "errno.h"
#include "rsvg.h"
#include "macro.h"

#include "string.h"
#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "inkface.h"
#include "common.h"
#include "canvas-x.h"

#ifdef HAS_XSP
#include <X11/extensions/Xsp.h>
int xsp_event_base=-1;
#endif // HAS_XSP

int GLOBAL_WIDTH = 0;
int GLOBAL_HEIGHT = 0;


//--------------
// X11 canvas
//--------------

static void 
canvas_init(
    canvas_t *canvas,
    int width, int height, 
    int fullscreen,
    paintfunc_t paint,
    void *paint_arg)
{
    int status = 0;
    Window rwin;
    int x=0, y=0;
    int screen = 0;

    x_canvas_t *self = (x_canvas_t *)canvas;

    ASSERT(self);
    self->width = GLOBAL_WIDTH = width;
    self->height = GLOBAL_HEIGHT = height;

    self->fullscreen = fullscreen;
    self->super.paint = paint;
    self->super.paint_arg = paint_arg;

    XInitThreads();

    ASSERT(self->dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(self->dpy));
    screen = DefaultScreen(self->dpy);
    ASSERT(screen >= 0);

    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;
    atoms_WINDOW_STATE
        = XInternAtom(self->dpy, "_NET_WM_STATE",False);
    ASSERT((atoms_WINDOW_STATE != BadAlloc && 
            atoms_WINDOW_STATE != BadValue));
    atoms_WINDOW_STATE_FULLSCREEN
        = XInternAtom(self->dpy, "_NET_WM_STATE_FULLSCREEN",False);
    ASSERT((atoms_WINDOW_STATE_FULLSCREEN != BadAlloc && 
            atoms_WINDOW_STATE_FULLSCREEN != BadValue));

    ASSERT(self->win = XCreateSimpleWindow(
                    self->dpy,
                    rwin,
                    x, y,
                    self->width, self->height,
                    0,
                    BlackPixel(self->dpy,screen),
                    BlackPixel(self->dpy,screen)));

    if(self->fullscreen){  
        /* Set the wmhints needed for fullscreen */
        status = XChangeProperty(self->dpy, self->win, 
                        atoms_WINDOW_STATE, XA_ATOM, 32,
                        PropModeReplace,
                        (unsigned char *) &atoms_WINDOW_STATE_FULLSCREEN, 1);
        ASSERT(status != BadAlloc);
        ASSERT(status != BadAtom);
        ASSERT(status != BadMatch);
        ASSERT(status != BadPixmap);
        ASSERT(status != BadValue);
        ASSERT(status != BadWindow);
    }

    //------------------------------------------
    // XSP extension - pressure sensitive input
    //------------------------------------------
    #ifdef HAS_XSP
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;
    /* get xsp event base */
    XSPQueryExtension(self->dpy,
                    &xsp_event_base,
                    &xsp_error_base,
                    &xsp_major,
                    &xsp_minor);
    ASSERT(xsp_event_base >= 0);

    XSPSetTSRawMode(self->dpy, True);
    #endif


    //--------------------------------
    // Double buffering support
    //--------------------------------
    #ifdef DOUBLE_BUFFER
    self->backBuffer = XdbeAllocateBackBufferName(self->dpy,self->win,XdbeBackground);
    self->swapinfo.swap_window = self->win;
    self->swapinfo.swap_action = XdbeBackground;
    #endif

    XClearWindow(self->dpy,self->win);

    self->surface = NULL;
    Visual *visual = DefaultVisual(self->dpy,DefaultScreen(self->dpy));
    ASSERT(visual)

    #ifdef DOUBLE_BUFFER
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->backBuffer, visual, self->width, self->height));
    #else
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->win, visual, self->width, self->height));
    #endif 
    ASSERT(self->ctx = cairo_create(self->surface));

    ASSERT(!pthread_mutex_init(&(self->super.dirt_mutex),NULL));


    // Fork a painter thread which does refresh jobs
    ASSERT(!pthread_mutex_init(&(self->super.paint_mutex),NULL));
    ASSERT(!pthread_cond_init(&(self->super.paint_condition),NULL));
    ASSERT(!pthread_create(&(self->super.painter_thr),NULL,painter_thread,self));

}

void canvas_show(canvas_t *canvas)
{
    x_canvas_t *self = (x_canvas_t *)canvas;
    // Map the window so that it's visible
    XMapWindow(self->dpy, self->win);
    XFlush(self->dpy);
    self->super.inc_dirt_count((canvas_t *)self,1);
}

void canvas_refresh(canvas_t *canvas)
{

}
                    
void canvas_cleanup(canvas_t *canvas)
{
    x_canvas_t *self = (x_canvas_t *)canvas;
    rsvg_term();

    self->super.shutting_down = TRUE;

    // Let's wait for the painter_thread to exit
    // before we destroy the X cairo surface on which it
    // might be drawing
    //
    ASSERT(!pthread_join(self->super.painter_thr,NULL));
    
    ASSERT(!pthread_mutex_destroy(&(self->super.paint_mutex)));
    ASSERT(!pthread_cond_destroy(&(self->super.paint_condition)));

    #ifdef DOUBLE_BUFFER
    XdbeDeallocateBackBufferName(self->dpy,self->backBuffer);
    #endif
    XUnmapWindow(self->dpy,self->win);
    XDestroyWindow(self->dpy,self->win);
    XCloseDisplay(self->dpy);

}

void inc_dirt_count(canvas_t *canvas, int count)
{
    x_canvas_t *self = (x_canvas_t *)canvas;

    CHK_ERRNO(pthread_mutex_lock(&(self->super.dirt_mutex)));
    self->super.dirt_count += count;
    CHK_ERRNO(pthread_mutex_unlock(&(self->super.dirt_mutex)));
}

void dec_dirt_count(canvas_t *canvas, int count)
{
    x_canvas_t *self = (x_canvas_t *)canvas;

    CHK_ERRNO(pthread_mutex_lock(&(self->super.dirt_mutex)));
    self->super.dirt_count -= count;
    if(self->super.dirt_count < 0) {
        self->super.dirt_count = 0;
    }
    CHK_ERRNO(pthread_mutex_unlock(&(self->super.dirt_mutex)));
}

void canvas_draw_elem(canvas_t *canvas, Element *elem)
{
    x_canvas_t *self = (x_canvas_t *)canvas;
    ASSERT(self);
    ASSERT(elem);
    cairo_surface_t *surface = elem->surface;
    cairo_set_source_surface(self->ctx,surface,elem->x,elem->y);
    cairo_paint(self->ctx);
}

x_canvas_t *x_canvas_new(void)
{
    x_canvas_t *object = NULL;
    ASSERT(object = (x_canvas_t *)malloc(sizeof(x_canvas_t)));
    memset(object,0,sizeof(x_canvas_t));
    object->super.init = canvas_init;
    object->super.cleanup = canvas_cleanup;
    object->super.refresh = canvas_refresh;
    object->super.show = canvas_show;
    object->super.inc_dirt_count = inc_dirt_count;
    object->super.dec_dirt_count = dec_dirt_count;
    object->super.draw_elem = canvas_draw_elem;
    return object;
}


