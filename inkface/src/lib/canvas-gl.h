#ifndef __CANVAS_GL_H__
#define __CANVAS_GL_H__

#include "canvas-common.h"

typedef void (*displayfunc_t) (void);

typedef struct gl_canvas_s gl_canvas_t;

struct gl_canvas_s {

    canvas_t super;

    //------------
    // Members
    //------------
 
    int width;
    int height;
    int fullscreen;

    Display *dpy; 
    Window win;

    //------------
    // Methods
    //------------
    displayfunc_t display;
    void (* register_display_function)(gl_canvas_t *, displayfunc_t);
};

gl_canvas_t *gl_canvas_new(void);

#endif //__CANVAS_GL_H__
