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

#ifdef ENABLE_PROFILING
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

#endif


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


gint
compare_element(
    gconstpointer a, 
    gconstpointer b)
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
    int xsp_event_base=-1;
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;


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

    /*
     * Create X window of the size of the image
     */
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

    /*
     * Create Element objects from the loaded SVG
     */

    GList *eidList = inkface_get_element_ids(handle->priv->defs);
    GList *head_eidList = eidList;

    GList *elemList = NULL;
    Element *element = NULL;

    while(eidList){

        ASSERT(eidList->data);

        element = (Element *)g_malloc(sizeof(Element));
        memset(element,0,sizeof(Element));
        strncpy(element->name,"#",1);
        strncat(element->name,eidList->data,30);

        inkface_get_element(handle,element);

        elemList = g_list_prepend(elemList,element);

        g_free(eidList->data);
        eidList = eidList->next;
    }
    g_list_free(head_eidList);


    /*
     * Draw the sorted list of Elements
     */
    GList *sortedElemList = g_list_sort(elemList,compare_element);
    GList *elem = sortedElemList;
    while(elem)
    {
        Element *element = (Element *)elem->data;

        ASSERT(element);

        if(element->transient)
            goto next;

        if(!strncmp(element->name,"#rect7058",9)){
            // Use this element surface as mask
            int cover_w=1,cover_h=1;

            cairo_surface_t *cover_surface =
                cairo_image_surface_create_from_png(
                "/photos/inkfun/corrs.png");
            cover_w = cairo_image_surface_get_width(cover_surface);
            cover_h = cairo_image_surface_get_height(cover_surface);
            cairo_save(ctx);
            cairo_scale(ctx,
                        element->w*1./cover_w,
                        element->h*1./cover_h);
            cairo_set_source_surface(ctx,
                        cover_surface, 
                        element->x*cover_w*1./element->w,
                        element->y*cover_h*1./element->h);
            
            cairo_paint(ctx);
            cairo_restore(ctx);

            // apply the mask
            cairo_set_source_rgb(ctx,0,0,0);
            cairo_mask_surface(ctx,element->surface,
                        element->x,
                        element->y);
            cairo_fill(ctx);
        } else {
            cairo_set_source_surface(ctx,
                element->surface,element->x,element->y);
            cairo_paint(ctx);
        }
        cairo_surface_destroy(element->surface);

        next:
            g_free(elem->data);
            elem = elem->next;
    }
    g_list_free(elemList);

    XFlush(dpy);

    /*
     * Setup the event listening
     */
    XSelectInput(dpy, win, StructureNotifyMask);
    XSelectInput(dpy, win, StructureNotifyMask|PointerMotionMask);
    while(1)
    {
        XMotionEvent *mevent;
        XEvent event;
        XNextEvent(dpy,&event);
        switch(event.type){
        case MapNotify:
            break;
        case MotionNotify:
            mevent = (XMotionEvent *)(&event);
            /*
             * Trigger the events in decreasing "order" of the elements
             */
            GList *elem = g_list_last(sortedElemList);
            while(elem){
                Element *el = (Element *)(elem->data);
                if(el->transient){
                    elem = elem->prev;
                    continue;
                }
                if((mevent->x > el->x) &&
                    (mevent->y > el->y) &&
                    (mevent->x < (el->x+el->w)) &&
                    (mevent->y < (el->y+el->h)))
                {
                    printf("%s under mouse\n",el->name);
                }
                elem = elem->prev;
            }
            break;
        default:
            break;
        }
    }


    rsvg_term ();

    return 0;
}
