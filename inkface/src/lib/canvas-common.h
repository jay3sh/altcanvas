#ifndef __CANVAS_COMMON_H__
#define __CANVAS_COMMON_H__

typedef struct canvas_s canvas_t;

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
 
    // Painting control members
    int dirt_count;
    unsigned int timer_step;
    int timer_counter;
    pthread_mutex_t paint_mutex;
    pthread_cond_t paint_condition;
    pthread_mutex_t dirt_mutex;
    pthread_t painter_thr;

    int shutting_down;

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

#endif // __CANVAS_COMMON_H__
