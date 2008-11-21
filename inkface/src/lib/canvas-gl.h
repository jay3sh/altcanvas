#ifndef __CANVAS_GL_H__
#define __CANVAS_GL_H__

#include "canvas-common.h"

typedef struct gl_canvas_s gl_canvas_t;

struct gl_canvas_s {

    canvas_t super;

    //------------
    // Members
    //------------
 
    int width;
    int height;
    int fullscreen;

    // Painting control members
    int dirt_count;
    unsigned int timer_step;
    int timer_counter;
    pthread_mutex_t paint_mutex;
    pthread_cond_t paint_condition;
    pthread_mutex_t dirt_mutex;
    pthread_t painter_thr;

    int shutting_down;

};

gl_canvas_t *gl_canvas_new(void);

#endif //__CANVAS_GL_H__
