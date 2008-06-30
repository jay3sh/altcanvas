#include "stdio.h"
#include "stdlib.h"
#include "unistd.h"

#include <X11/Xlib.h>
#include <X11/Xatom.h>

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
    int xres;
    int yres;
    Pixmap pix;
    XGCValues gcv;
    GC gc;
    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;


    ASSERT(dpy = XOpenDisplay(NULL));


    atoms_WINDOW_STATE
        = XInternAtom(dpy, "_NET_WM_STATE",False);
    atoms_WINDOW_STATE_FULLSCREEN
        = XInternAtom(dpy, "_NET_WM_STATE_FULLSCREEN",False);

    screen = DefaultScreen(dpy);
    ASSERT(rwin = RootWindow(dpy,screen));
    xres   = ScreenOfDisplay (dpy, screen)->width;
    yres   = ScreenOfDisplay (dpy, screen)->height;

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    0, 0,
                    xres, yres,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    XChangeProperty(dpy, win, atoms_WINDOW_STATE, XA_ATOM, 32,
                  PropModeReplace,
                  (unsigned char *) &atoms_WINDOW_STATE_FULLSCREEN, 1);

    XMapWindow(dpy, win);

    gcv.foreground = WhitePixel(dpy,screen);
    ASSERT(gc = XCreateGC(dpy,win,GCForeground,&gcv));

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

    XFillRectangle(dpy,win,gc,x,y,w/2,h/2);

    XFlush(dpy);

    usleep(2*1000*1000);
    XCloseDisplay(dpy);

    return 0;
}
