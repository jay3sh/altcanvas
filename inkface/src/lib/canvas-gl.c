
#include "errno.h"
#include "rsvg.h"
#include "macro.h"

#include "string.h"
#include <cairo.h>
#include <cairo-xlib.h>

#include "inkface.h"
#include "common.h"
#include "canvas-gl.h"

//-------------------
// OpenGL canvas
//-------------------

#ifdef HAS_OPENGL

#include <GL/gl.h>
#include <GL/glx.h>

extern int GLOBAL_WIDTH;
extern int GLOBAL_HEIGHT;

#ifdef GL_VERSION_1_1
static GLuint texName;
#endif
static int checkImageWidth = 800;
static int checkImageHeight = 480;
static GLubyte checkImage[800][480][4];
void glinit(void)
{    
   glClearColor (0.0, 0.0, 0.0, 0.0);
   glShadeModel(GL_FLAT);
   glEnable(GL_DEPTH_TEST);

   glPixelStorei(GL_UNPACK_ALIGNMENT, 1);

#ifdef GL_VERSION_1_1
   glGenTextures(1, &texName);
   glBindTexture(GL_TEXTURE_2D, texName);
#endif

   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT);
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT);
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST);
   glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST);
#ifdef GL_VERSION_1_1
   glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, checkImageWidth, checkImageHeight, 
                0, GL_RGBA, GL_UNSIGNED_BYTE, checkImage);
#else
   glTexImage2D(GL_TEXTURE_2D, 0, 4, checkImageWidth, checkImageHeight, 
                0, GL_RGBA, GL_UNSIGNED_BYTE, checkImage);
#endif
}


static void
canvas_init(
    canvas_t *canvas,
    int width,
    int height,
    int fullscreen)
{
    Window rwin;
    int screen = 0;
    int attrib[] = { GLX_RGBA,
		    GLX_RED_SIZE, 1,
		    GLX_GREEN_SIZE, 1,
		    GLX_BLUE_SIZE, 1,
		    GLX_DOUBLEBUFFER,
		    None };
    XVisualInfo *visinfo = NULL;
    unsigned long mask;
    GLXContext glctx;
    XSetWindowAttributes attr;
 
    gl_canvas_t *self = (gl_canvas_t *) canvas;
    ASSERT(self);
    self->width = GLOBAL_WIDTH = width;
    self->height = GLOBAL_HEIGHT = height;

    self->fullscreen = fullscreen;

    ASSERT(self->dpy = XOpenDisplay(0));
    screen = DefaultScreen(self->dpy);
    rwin = RootWindow(self->dpy,screen);

    ASSERT(visinfo = glXChooseVisual( self->dpy, screen, attrib ));
    /* window attributes */
    attr.background_pixel = 0;
    attr.border_pixel = 0;
    attr.colormap = XCreateColormap(self->dpy,rwin,visinfo->visual,AllocNone);
    attr.event_mask = StructureNotifyMask | ExposureMask;
    mask = CWBackPixel | CWBorderPixel | CWColormap | CWEventMask;

    ASSERT(self->win = XCreateWindow( self->dpy, rwin, 0, 0, 
                self->width, self->height,
		        0, visinfo->depth, InputOutput,
		        visinfo->visual, mask, &attr ));

    ASSERT(glctx = glXCreateContext(self->dpy, visinfo, NULL, True ));

    glXMakeCurrent( self->dpy, self->win, glctx );

    glinit();
}

static void canvas_show(canvas_t *canvas)
{
    gl_canvas_t *self = (gl_canvas_t *)canvas;
    XMapWindow(self->dpy, self->win);
    XFlush(self->dpy);
    canvas->inc_dirt_count(canvas,1);
}

static void canvas_refresh(canvas_t *self)
{

}
                    
static void canvas_cleanup(canvas_t *canvas)
{
    gl_canvas_t *self = (gl_canvas_t *)canvas;
    rsvg_term();

    self->super.shutting_down = TRUE;


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

static void canvas_draw_elem(canvas_t *canvas, Element *elem)
{
    unsigned char *surfData = NULL;
    gl_canvas_t *self = (gl_canvas_t *)canvas;
    ASSERT(self);
    ASSERT(elem);

    surfData = cairo_image_surface_get_data(surface);

    glPushMatrix();
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, elem->width, elem->height, 
                0, GL_RGBA, GL_UNSIGNED_BYTE, surfData);

    glPopMatrix();
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
