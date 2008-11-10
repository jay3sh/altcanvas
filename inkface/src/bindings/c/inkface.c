
#include "string.h"
#include <cairo.h>
#include <cairo-xlib.h>

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "inkface.h"
#include "common.h"
#include "cinkface.h"

RsvgHandle *handle = NULL;
Canvas_t *x_canvas = NULL;

void paint(void *arg);

GList *inkface_loadsvg(char *svgname)
{
    // Create rsvg handle for the SVG file
    ASSERT(handle = rsvg_handle_from_file(svgname));
    GList *elist = load_element_list(handle);
    return elist;
}

Canvas_t *
inkface_create_X_canvas(int width,int height,int fullscreen)
{
    int fschoice = FALSE;

    x_canvas = (Canvas_t *)malloc(sizeof(Canvas_t));
    memset(x_canvas,0,sizeof(Canvas_t));

    canvas_t *cobject = canvas_new();
    ASSERT(cobject);    

    //
    // Fullscreen preferences:
    //
    // 1. env var INKFACE_FULLSCREEN 
    // 2. kwd arg fullscreen 
    //
    char *env_fullscreen = getenv("INKFACE_FULLSCREEN");
    fschoice = (env_fullscreen && !strncmp(env_fullscreen,"TRUE",4)) || \
                    fullscreen;
     
    cobject->init(cobject,width,height,fschoice,paint,(void *)x_canvas);

    return x_canvas;
}

void paint(void *arg)
{
}

inkface_init(void)
{
    rsvg_init();
}
