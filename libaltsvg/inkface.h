
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
    char name[16];
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

#endif /*__INKFACE_H__ */
