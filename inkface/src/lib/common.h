
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
typedef void (*incdcfunc_t) (canvas_t *self, int count);
typedef void (*decdcfunc_t) (canvas_t *self, int count);

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
    incdcfunc_t inc_dirt_count;
    decdcfunc_t dec_dirt_count;
    paintfunc_t paint;

};

canvas_t *canvas_new(void);

void * painter_thread(void *arg);

#define REFRESH_INTERVAL_MSEC 50


#endif /* __COMMON_H__ */