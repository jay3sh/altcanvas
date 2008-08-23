#include "rsvg.h"
#include "rsvg-cairo.h"
#include "rsvg-cairo-draw.h"
#include "rsvg-cairo-render.h"
#include "rsvg-styles.h"
#include "rsvg-structure.h"

struct _RsvgNodeRect {
    RsvgNode super;
    RsvgLength x, y, w, h, rx, ry;
    gboolean got_rx, got_ry;
};

typedef struct _RsvgNodeRect RsvgNodeRect;

#include "stdlib.h"
#include "string.h"

#include <cairo.h>
#include <cairo-xlib.h>

#include <inkface.h>


#define ASSERT(x) \
        if (!(x)) { \
           printf("Assertion failed: %s:%d <<%s>>\n", \
                __FILE__,__LINE__,__FUNCTION__); \
           exit(1); \
        }

/* Constructor and Destructor Prototypes */

void main_constructor( void )
__attribute__ ((no_instrument_function, constructor));

void main_destructor( void )
__attribute__ ((no_instrument_function, destructor));

void __cyg_profile_func_enter( void *func_address, void *call_site )
__attribute__ ((no_instrument_function));

void __cyg_profile_func_exit ( void *func_address, void *call_site )
__attribute__ ((no_instrument_function));


/* Output trace file pointer */
static FILE *fp;

void main_constructor( void )
{
  fp = fopen( "trace.txt", "w" );
    if (fp == NULL) exit(-1);
}


void main_deconstructor( void )
{
  fclose( fp );
}

void __cyg_profile_func_enter( void *this, void *callsite )
{
   /* Function Entry Address */
   fprintf(fp, "E%p\n", (int *)this);
}


void __cyg_profile_func_exit( void *this, void *callsite )
{
   /* Function Exit Address */
   fprintf(fp, "X%p\n", (int *)this);
}


RsvgHandle *
rsvg_handle_from_file(const char *filename)
{
    GByteArray *bytes = NULL;
    RsvgHandle *handle = NULL;
    guchar buffer[4096];
    FILE *f;
    int length;

    ASSERT(f = fopen(filename,"rb"));
    ASSERT(bytes = g_byte_array_new());
    while (!feof (f)) {
        length = fread (buffer, 1, sizeof (buffer), f);
        if(length > 0){
            if (g_byte_array_append (bytes, buffer, length) == NULL) {
                fclose (f);
                g_byte_array_free (bytes, TRUE);
                return NULL;
            }
        } else if (ferror (f)) {
            fclose (f);
            g_byte_array_free (bytes, TRUE);
            return NULL;
        }
    }
    fclose(f);

    ASSERT(handle = rsvg_handle_new());
    rsvg_handle_set_base_uri (handle, filename);
    ASSERT(rsvg_handle_write(handle,bytes->data,bytes->len,NULL));
    ASSERT(rsvg_handle_close(handle,NULL));
    
    return handle;
}

void get_node_dimensions(
    RsvgHandle *handle, const char *id,double *w, double *h)
{
    RsvgNode *childNode = NULL;

    ASSERT(id)    
    ASSERT(handle)    
    ASSERT(childNode = rsvg_defs_lookup (handle->priv->defs, id))

    gchar *nodeType = childNode->type->str;
    if(!strcmp(nodeType,"g")){
        
    }
}

void
get_rect_node_dimensions(
    RsvgHandle *handle, const char *id,double *w, double *h)
{
    RsvgNode *childNode = NULL;

    ASSERT(id)    
    ASSERT(handle)    
    ASSERT(childNode = rsvg_defs_lookup (handle->priv->defs, id))
    printf("node type = %s\n",childNode->type->str);

    RsvgNodeRect *rectNode = NULL;
    rectNode = (RsvgNodeRect *)childNode;

    *w = rectNode->w.length;
    *h = rectNode->h.length;

    return;
}


void test1(void)
{
    #define W_WIDTH 800
    #define W_HEIGHT 480

    Window win,rwin;
    Display *dpy=NULL;
    int screen = 0;
    int w=800, h=480;
    int x=0, y=0;
    Pixmap pix;
    XGCValues gcv;
    GC gc;

    ASSERT(dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(dpy));
    screen = DefaultScreen(dpy);

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    x, y,
                    W_WIDTH,W_HEIGHT,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    XClearWindow(dpy,win);
    XMapWindow(dpy, win);

    cairo_surface_t *surface = NULL;
    cairo_t *cr = NULL;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    ASSERT(surface = cairo_xlib_surface_create(
                        dpy, win, visual, W_WIDTH,W_HEIGHT));
    ASSERT(cr = cairo_create(surface));


    cairo_surface_t *source_surface = NULL;
    cairo_t *source_cr = NULL;
    ASSERT(source_surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, W_WIDTH, W_HEIGHT))
    ASSERT(source_cr = cairo_create(source_surface))

    //cairo_rectangle(source_cr,20,20,50,50);
    //cairo_clip(source_cr);

    cairo_set_source_rgb(source_cr,0.8,0.4,0.9);
    cairo_rectangle(source_cr,20,20,100,100);
    cairo_stroke(source_cr);


    cairo_set_source_surface(source_cr,source_surface,0,0);
    cairo_translate(source_cr,0,200);
    cairo_paint(source_cr);

    //double x1,x2,y1,y2;
    //cairo_clip_extents(source_cr,&x1,&y1,&x2,&y2);
    //printf("clip %f,%f,%f,%f\n",x1,y1,x2,y2);

    cairo_set_source_surface(cr,source_surface,0,0);
    cairo_paint(cr);

    XFlush(dpy);

    sleep(1);
}

gint
compare_element(
    gconstpointer a, 
    gconstpointer b,
    gpointer user_data)
{
    Element *eA=NULL,*eB=NULL;
    eA = (Element *)a;
    eB = (Element *)b;
    return(eA->order - eB->order);
}

int main(int argc, char *argv[])
{

    Window win,rwin;
    Display *dpy=NULL;
    int screen = 0;
    int w=800, h=480;
    int x=0, y=0;
    Pixmap pix;
    XGCValues gcv;
    GC gc;
    char *elemChoice = NULL;


    if(argc < 2){
        printf("%s <svg-filepath>\n",argv[0]);
        exit(0);
    }

    /*
     * Load SVG file
     */
    RsvgHandle *handle = NULL;
    rsvg_init ();

    ASSERT(handle = rsvg_handle_from_file(argv[1]));

    if(argc == 3){
        elemChoice = argv[2];
    }

    RsvgDimensionData dim;
    rsvg_handle_get_dimensions(handle,&dim);


    ASSERT(dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(dpy));
    screen = DefaultScreen(dpy);

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    x, y,
                    dim.width, dim.height,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    XClearWindow(dpy,win);
    XMapWindow(dpy, win);

    cairo_surface_t *surface = NULL;
    cairo_t *ctx = NULL;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    ASSERT(surface = cairo_xlib_surface_create(
                        dpy, win, visual, dim.width,dim.height));
    ASSERT(ctx = cairo_create(surface));


    cairo_surface_t *node_surface = NULL;

    GList *eidList = rsvg_get_ids(handle->priv->defs);
    GList *head_eidList = eidList;

    GList *elemList = NULL;
    Element *element = NULL;

    while(eidList){
            /*
            if(elemChoice){
                if(strcmp(elemChoice,eidList->data)){
                    printf("Skipping %s\n",eidList->data);
                    g_free(eidList->data);
                    eidList = eidList->next;
                    continue;
                }
            }
            */

        ASSERT(eidList->data);

        element = (Element *)g_malloc(sizeof(Element));
        memset(element,0,sizeof(Element));
        strncpy(element->name,"#",1);
        strncat(element->name,eidList->data,30);

        get_element(handle,element);

        elemList = g_list_prepend(elemList,element);

            /*
            printf("%d] Drawing %s\n",element.order,eidList->data);
            */
        g_free(eidList->data);
        eidList = eidList->next;
    }
    g_list_free(head_eidList);


    GList *elem = g_list_sort(elemList,compare_element);
    while(elem)
    {
        Element *element = (Element *)elem->data;

        ASSERT(element);

        cairo_set_source_surface(ctx,element->surface,element->x,element->y);
        cairo_paint(ctx);
        cairo_surface_destroy(element->surface);

        g_free(elem->data);

        elem = elem->next;
    }
    g_list_free(elemList);

    XFlush(dpy);

    sleep(3);

    rsvg_term ();
}
