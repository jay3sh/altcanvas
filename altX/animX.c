#include "stdio.h"
#include <cairo.h>
#include <cairo-xlib.h>

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d\n",__FILE__,__LINE__); \
           exit(1); \
        }

int main(int argc, char *argv[])
{
    Window win,rwin;
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

    XSelectInput(dpy, win, StructureNotifyMask);

    while(1)
    {
        XEvent event;

        XNextEvent(dpy, &event);
        if (event.type == MapNotify)
            break;
    }

    printf("Filling!\n");

    /*
     * CAIRO Drawing
     */
    cairo_surface_t *surface;
    cairo_t *cr;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));

    XClearWindow(dpy, win);
    surface = cairo_xlib_surface_create(dpy, win, visual, w,h);
    cr = cairo_create(surface);

    cairo_set_source_rgb(cr, 0.8, 0.8, 0.8);

    #define SIZE 20
    cairo_rectangle(cr,10,10,SIZE,SIZE);
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
