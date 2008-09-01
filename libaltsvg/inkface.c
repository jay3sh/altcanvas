#include "rsvg.h"
#include "rsvg-cairo.h"
#include "rsvg-cairo-draw.h"
#include "rsvg-cairo-render.h"
#include "rsvg-styles.h"
#include "rsvg-structure.h"

#include "config.h"
#include "stdlib.h"
#include "string.h"

#include <cairo.h>
#include <cairo-xlib.h>

#include <inkface.h>

#include <sys/time.h>
#include <time.h>
#include "pthread.h"
#include "errno.h"




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

cairo_t *ctx = NULL;
Display *dpy=NULL;
Window win;

GList *sortedElemList = NULL;

gboolean inkface_dirty = TRUE;
pthread_mutex_t inkface_dirty_mutex;

pthread_mutex_t paint_mutex;
pthread_cond_t paint_condition;

void
signal_paint()
{
    pthread_cond_signal(&paint_condition);
}


void
paint(void *arg)
{
    GList *elem = sortedElemList;
    while(elem)
    {
        Element *element = (Element *)elem->data;

        ASSERT(element);

        if(element->type == ELEM_TYPE_TRANSIENT) goto next;

        if((element->type == ELEM_TYPE_MASK) &&
            (element->name) && 
            !strncmp(element->name,
                "currentCoverMask",strlen("currentCoverMask")))
        {
            // Use this element surface as mask
            int cover_w=1,cover_h=1;

            char *center_img_path = getenv("CENTER_COVER_ART");

            if(!center_img_path) goto next;

            cairo_surface_t *cover_surface =
                cairo_image_surface_create_from_png(
                center_img_path);
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
            ASSERT(cairo_surface_status(element->surface) == 
                    CAIRO_STATUS_SUCCESS)
            cairo_set_source_surface(ctx,
                element->surface,element->x,element->y);
            cairo_paint(ctx);
        }

        next:
            elem = elem->next;
    }

    XFlush(dpy);
}

void *
painter_thread(void *arg)
{
    int rc=0;

    while(1)
    {
        paint(NULL);
        rc=pthread_cond_wait(&paint_condition,&paint_mutex);
        ASSERT(!rc);
    }

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


void eventloop()
{
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
                gboolean nowInFocus = FALSE;
                Element *el = (Element *)(elem->data);
                if(el->type == ELEM_TYPE_TRANSIENT){
                    elem = elem->prev;
                    continue;
                }
                if((mevent->x > el->x) &&
                    (mevent->y > el->y) &&
                    (mevent->x < (el->x+el->w)) &&
                    (mevent->y < (el->y+el->h)))
                {
                    nowInFocus = TRUE;
                } 

                if(el->inFocus && !nowInFocus){
                    if(el->onMouseLeave) el->onMouseLeave(el,sortedElemList);
                }
                if(!el->inFocus && nowInFocus){
                    if(el->onMouseEnter) el->onMouseEnter(el,sortedElemList);
                }

                el->inFocus = nowInFocus;

                elem = elem->prev;
            }
            break;
        default:
            break;
        }
    }

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

RsvgHandle *handle = NULL;

void init_backend(const char* svgfilename)
{
    ASSERT(svgfilename);

    Window rwin;
    int screen = 0;
    int w=800, h=480;
    int x=0, y=0;
    Pixmap pix;
    XGCValues gcv;
    GC gc;
    int xsp_event_base=-1;
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;

    /* Setup X for multithreaded environment */
    XInitThreads();

    /*
     * Load SVG file
     */
    rsvg_init ();

    ASSERT(handle = rsvg_handle_from_file(svgfilename));

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
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    ASSERT(surface = cairo_xlib_surface_create(
                        dpy, win, visual, dim.width,dim.height));
    ASSERT(ctx = cairo_create(surface));

}

void cleanup_backend()
{
    //TODO cleanup element list
    rsvg_term ();

}

GList *
load_element_list()
{
    /*
     * Create Element objects from the loaded SVG
     */

    GList *eidList = inkface_get_element_ids(handle->priv->defs);
    ASSERT(eidList);

    GList *head_eidList = eidList;

    GList *elemList = NULL;
    Element *element = NULL;

    while(eidList){

        ASSERT(eidList->data);

        element = (Element *)g_malloc(sizeof(Element));
        memset(element,0,sizeof(Element));
        strncpy(element->id,"#",1);
        strncat(element->id,eidList->data,30);  //TODO macro

        inkface_get_element(handle,element);

        elemList = g_list_prepend(elemList,element);

        g_free(eidList->data);
        eidList = eidList->next;
    }
    g_list_free(head_eidList);

    ASSERT(sortedElemList = g_list_sort(elemList,compare_element));

    return sortedElemList;
}

void 
fork_painter_thread()
{
    /*
     * Fork a thread to draw the sorted element list
     */
    pthread_mutex_init(&inkface_dirty_mutex,NULL);
    pthread_t thr;
    pthread_create(&thr,NULL,painter_thread,NULL);

}

int main(int argc, char *argv[])
{


    if(argc < 2){
        printf("%s <svg-filepath>\n",argv[0]);
        exit(0);
    }

    init_backend(argv[1]);

    GList *element_list = load_element_list();
    /*
     * Wire the logic defined in event handlers with Elements
     */
    wire_logic(sortedElemList);

    fork_painter_thread();
    /*
     * Consume events infinitely
     */
    eventloop();

    return 0;
}
