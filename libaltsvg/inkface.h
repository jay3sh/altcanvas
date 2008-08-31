
#ifndef __INKFACE_H__
#define __INKFACE_H__

#include "cairo.h"

typedef struct _Element Element;

struct _Element{
    cairo_t *cr;
    cairo_surface_t *surface;
    int x;
    int y;
    int w;
    int h;
    int order;
    char *name;
    char id[16];
    gboolean transient;

    gboolean inFocus;

    void (*onMouseEnter)(Element *self);
};


typedef struct _InkfaceState InkfaceState;

struct _InkfaceState {
    char *name;                 /* user friendly name */
    guint16 order;              /* Order to draw */
    gboolean transient;         /* If transient, it will be visible 
                                   only programmatically */
};


void wire_logic(GList *);
void inkface_istate_finalize (InkfaceState *);
void inkface_istate_init(InkfaceState *);


#define LOG(...) \
    fprintf(strerr,"[%s:%d] ",__FILE__,__LINE__); \
    fprintf(stderr,__VA_ARGS__); 

#endif /*__INKFACE_H__ */
