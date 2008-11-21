#ifndef __CANVAS_X_H__
#define __CANVAS_X_H__

#include "canvas-common.h"

typedef void (*paintfunc_t) (void *arg);

typedef struct x_canvas_s x_canvas_t;

struct x_canvas_s {

    canvas_t super;

    //------------
    // Members
    //------------

    int width;
    int height;
    int fullscreen;

    Display *dpy; 
    cairo_t *ctx;
    cairo_surface_t *surface;
    Window win;

    #ifdef DOUBLE_BUFFER
    XdbeBackBuffer backBuffer;
    XdbeSwapInfo swapinfo;
    #endif

    //------------
    // Methods
    //------------
    paintfunc_t paint;
    void *paint_arg;
    void (* register_paint_function)(x_canvas_t *,paintfunc_t,void *);

};

x_canvas_t *x_canvas_new(void);


#endif // __CANVAS_X_H__
