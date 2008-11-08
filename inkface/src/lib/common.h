
#ifndef __COMMON_H__
#define __COMMON_H__

RsvgHandle *rsvg_handle_from_file(const char *filename);

typedef struct canvas_s canvas_t;
typedef struct element_s element_t;

typedef void (*paintfunc_t) (void *arg);
typedef void (*initfunc_t) (canvas_t *self,
                    int width, int height, int fullscreen,
                    paintfunc_t,void *);
typedef void (*cleanupfunc_t) (canvas_t *self);
typedef void (*drawfunc_t) (canvas_t *self, element_t *element);
typedef void (*refreshfunc_t) (canvas_t *self);
typedef void (*showfunc_t) (canvas_t *self);
typedef void (*incdcfunc_t) (canvas_t *self, int count);
typedef void (*decdcfunc_t) (canvas_t *self, int count);
typedef void (*draw_elem_t) (canvas_t *self, Element *elem);

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
    pthread_t painter_thr;

    int shutting_down;

    #ifdef DOUBLE_BUFFER
    XdbeBackBuffer backBuffer;
    XdbeSwapInfo swapinfo;
    #endif

    void *paint_arg;

    //------------
    // Methods
    //------------

    initfunc_t init;
    cleanupfunc_t cleanup;
    drawfunc_t draw;
    refreshfunc_t refresh;
    showfunc_t show;
    incdcfunc_t inc_dirt_count;
    decdcfunc_t dec_dirt_count;
    paintfunc_t paint;
    draw_elem_t draw_elem;

};

canvas_t *canvas_new(void);


void * painter_thread(void *arg);

#define REFRESH_INTERVAL_MSEC 50

#define POINTER_STATE_TAP       0x1
#define POINTER_STATE_ENTER     0x2
#define POINTER_STATE_LEAVE     0x4

#define DUP_TAP_IGNORANCE_LIMIT 1

int process_motion_event(Element *el,XMotionEvent *mevent);
int calculate_pressure(Element *el, XEvent *event);

#ifdef HAS_XSP

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
  * x = GLOBAL_WIDTH - (GLOBAL_WIDTH * *x) / DEV_X_DELTA;\
  * y = GLOBAL_HEIGHT - (GLOBAL_HEIGHT * *y) / DEV_Y_DELTA;\
}

#endif /* HAS_XSP */

#endif /* __COMMON_H__ */
