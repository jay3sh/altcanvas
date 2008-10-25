
#ifndef __COMMON_H__
#define __COMMON_H__

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

RsvgHandle *rsvg_handle_from_file(const char *filename);

typedef struct canvas_s canvas_t;
typedef struct element_s element_t;

struct canvas_s {

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

    // Painting control members
    int dirt_count;
    unsigned int timer_step;
    int timer_counter;
    pthread_mutex_t paint_mutex;
    pthread_cond_t paint_condition;
    pthread_mutex_t dirt_mutex;

    #ifdef DOUBLE_BUFFER
    XdbeBackBuffer backBuffer;
    XdbeSwapInfo swapinfo;
    #endif

    //------------
    // Methods
    //------------

    void (*draw) (canvas_t *canvas, element_t *element);
    void (*inc_dirt_count) (canvas_t *canvas, int count);
    void (*dec_dirt_count) (canvas_t *canvas, int count);
};


#endif /* __COMMON_H__ */
