

#include "errno.h"
#include "rsvg.h"
#include "macro.h"

#include "string.h"
#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "inkface.h"
#include "common.h"
#include "canvas-gl.h"

#include <GL/glut.h>

//-------------------
// OpenGL canvas
//-------------------

#ifdef USE_OPENGL

static void
canvas_init(
    canvas_t *canvas,
    int width,
    int height,
    int fullscreen)
{
    gl_canvas_t *self = (gl_canvas_t *)canvas;
    /*
    glutInit(NULL, NULL);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(250, 250);
    glutInitWindowPosition(100, 100);
    glutCreateWindow("inkface");
    */
    //init();
    //glutDisplayFunc(display);
    //glutReshapeFunc(reshape);
    //glutKeyboardFunc(keyboard);
}

static void canvas_show(canvas_t *self)
{

}

static void canvas_refresh(canvas_t *self)
{

}
                    
static void canvas_cleanup(canvas_t *self)
{

}

static void inc_dirt_count(canvas_t *self, int count)
{
    CHK_ERRNO(pthread_mutex_lock(&(self->dirt_mutex)));
    self->dirt_count += count;
    CHK_ERRNO(pthread_mutex_unlock(&(self->dirt_mutex)));
}

static void dec_dirt_count(canvas_t *self, int count)
{
    CHK_ERRNO(pthread_mutex_lock(&(self->dirt_mutex)));
    self->dirt_count -= count;
    if(self->dirt_count < 0) {
        self->dirt_count = 0;
    }
    CHK_ERRNO(pthread_mutex_unlock(&(self->dirt_mutex)));
}

static void canvas_draw_elem(canvas_t *self, Element *elem)
{

}

gl_canvas_t *gl_canvas_new(void)
{
    gl_canvas_t *object = NULL;
    ASSERT(object = (gl_canvas_t *)malloc(sizeof(gl_canvas_t)));
    memset(object,0,sizeof(gl_canvas_t));

    object->super.init = canvas_init;
    object->super.cleanup = canvas_cleanup;
    object->super.refresh = canvas_refresh;
    object->super.show = canvas_show;
    object->super.inc_dirt_count = inc_dirt_count;
    object->super.dec_dirt_count = dec_dirt_count;
    object->super.draw_elem = canvas_draw_elem;
 
    return object;
}

#endif // USE_OPENGL
