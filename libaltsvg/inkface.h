
#ifndef __INKFACE_H__
#define __INKFACE_H__

#include "rsvg.h"
#include "stdlib.h"
#include "cairo.h"

typedef struct _Element Element;

typedef enum { ELEM_TYPE_MASK=1, 
                ELEM_TYPE_TRANSIENT=2 } element_type_t;

struct _Element{
    cairo_t *cr;
    cairo_surface_t *surface;
    int x;
    int y;
    int w;
    int h;
    int order;
    char *name;
    char id[32];
    element_type_t type;
    char *on_mouse_over;

    gboolean inFocus;

    void (*onMouseEnter)(Element *self, void *userdata);
    void (*onMouseLeave)(Element *self, void *userdata);

};


typedef struct _InkfaceState InkfaceState;

struct _InkfaceState {
    char *name;                 /* user friendly name */
    guint16 order;              /* Order to draw */
    char *on_mouse_over;
    element_type_t type; 
};

void inkface_istate_finalize (InkfaceState *);
void inkface_istate_init(InkfaceState *);

#define LOG(...) \
    fprintf(stderr,"[%s:%d] ",__FILE__,__LINE__); \
    fprintf(stderr,__VA_ARGS__); \
    fprintf(stderr,"\n"); 

#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d <<%s>>\n", \
                __FILE__,__LINE__,__FUNCTION__); \
           exit(1); \
        }

/* inkface functions */
void signal_paint();
void init_backend(const char* svgfilename);
void cleanup_backend();
GList *load_element_list();
void fork_painter_thread();

#endif /*__INKFACE_H__ */
