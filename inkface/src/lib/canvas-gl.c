

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

#ifdef HAS_OPENGL


#ifdef GL_VERSION_1_1
static GLuint texName;
#endif
static int checkImageWidth = 800;
static int checkImageHeight = 480;
static GLubyte checkImage[800][480][4];
void init(void)
{    
   glClearColor (0.0, 0.0, 0.0, 0.0);
   glShadeModel(GL_FLAT);
   glEnable(GL_DEPTH_TEST);

   //makeCheckImage();
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
    gl_canvas_t *self = (gl_canvas_t *)canvas;
    glutInit(NULL, NULL);
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
    glutInitWindowSize(250, 250);
    glutInitWindowPosition(100, 100);
    glutCreateWindow("inkface");
    //init();
    ASSERT(self->display);
    glutDisplayFunc(self->display);
    //glutReshapeFunc(reshape);
    //glutKeyboardFunc(keyboard);
}

static void 
canvas_register_display_function(
    gl_canvas_t *canvas,
    displayfunc_t display)
{
    canvas->display = display;
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
