#include "stdio.h"
#include "stdlib.h"
#include "unistd.h"
#include <cairo.h>
#include <cairo-xlib.h>

#include <X11/extensions/Xdbe.h>

#define DECLARE_P(type,var) \
            type* var = NULL;

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d\n",__FILE__,__LINE__); \
           exit(1); \
        }

int main(int argc, char *argv[])
{
    Window win,rwin,win2;
    Display *dpy=NULL;
    int screen = 0;
    int w=800, h=480;
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

    XSelectInput(dpy, win, StructureNotifyMask|PointerMotionMask);

    int keepLooping = 1;
    while(keepLooping)
    {
        XMotionEvent *mevent;
        XEvent event;

        XNextEvent(dpy, &event);
        switch(event.type){
        case MapNotify:
            printf("MapNotify received\n");
            keepLooping = 0;
            break;
        case MotionNotify:
            mevent = (XMotionEvent *)(&event);
            printf("MotionNotify received (%d,%d)\n",
                mevent->x,mevent->y);
            break;
        }
    }

    /*
     * CAIRO Drawing
     */
    DECLARE_P(cairo_surface_t,surface);
    DECLARE_P(cairo_t,ctx);
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    XClearWindow(dpy, win);
    ASSERT(surface =
        cairo_xlib_surface_create(dpy, win, visual, w,h));
    ASSERT(ctx =
        cairo_create(surface));


    // Create widget surface
    DECLARE_P(cairo_surface_t,wsurface)
    DECLARE_P(cairo_t,wctx)

    #define SIZE 50
    ASSERT(wsurface = cairo_image_surface_create(
                            CAIRO_FORMAT_ARGB32,
                            SIZE, SIZE));

    ASSERT(wctx = cairo_create(wsurface));

    cairo_set_source_rgb(wctx, 0.8, 0.8, 0.8);
    cairo_rectangle(wctx,10,10,SIZE,SIZE);
    cairo_fill(wctx);

    if (cairo_status(wctx)) {
        printf("Cairo is unhappy: %s\n",
            cairo_status_to_string (cairo_status (wctx)));
        exit(0);
    }

    int use_db  = 0;

    if((argc > 1)&&(argv[1][0] == 'Y')){
        use_db = 1;
    }

    if(use_db){
        win2 = XdbeAllocateBackBufferName(dpy,win,XdbeUndefined);
    } else {
        win2 = win;
    }

    XdbeSwapInfo swapinfo;
    swapinfo.swap_window = win;
    swapinfo.swap_action = XdbeUndefined;

    int i=0;
    for (; i<300; i++)
    {

        if(use_db){
            XdbeBeginIdiom(dpy);
        }

        //XFillRectangle(dpy,win2,gc,10+i,10+i,20,20);

        //XClearWindow(dpy, win);
        cairo_set_source_surface(ctx,wsurface,10+i,10+i);
        cairo_paint(ctx);

        if(use_db){
            XdbeSwapBuffers(dpy,&swapinfo,1);
        }

        XSync(dpy,0);

        if(use_db){
            XdbeEndIdiom(dpy);
        }

        XFlush(dpy);
        usleep(3*1000);
    }

    XFlush(dpy);

    cairo_destroy(wctx);
    cairo_surface_destroy(wsurface);
    cairo_destroy(ctx);
    cairo_surface_destroy(surface);
    XCloseDisplay(dpy);

    return 0;
}
