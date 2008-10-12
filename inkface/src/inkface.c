#include "rsvg.h"
//#include "rsvg-cairo.h"
//#include "rsvg-cairo-draw.h"
//#include "rsvg-cairo-render.h"
//#include "rsvg-styles.h"
//#include "rsvg-structure.h"

//#include "config.h"
#include "stdlib.h"
#include "string.h"

#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xdbe.h>

#include "inkface.h"

#include <sys/time.h>
#include <time.h>
#include "pthread.h"
#include "errno.h"

#define DOUBLE_BUFFER

#define REFRESH_INTERVAL_MSEC 80

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

gboolean inkface_dirt_count = 1;
pthread_mutex_t inkface_dirt_mutex;

pthread_mutex_t paint_mutex;
pthread_cond_t paint_condition;

XdbeBackBuffer backBuffer;
XdbeSwapInfo swapinfo;

void
signal_paint()
{
    pthread_cond_signal(&paint_condition);
}

/* Thread-safe routines to manipulate paint_mutex */
void incr_dirt_count(int count)
{
    pthread_mutex_lock(&inkface_dirt_mutex);
    inkface_dirt_count += count;
    pthread_mutex_unlock(&inkface_dirt_mutex);
}

void decr_dirt_count(int count)
{
    pthread_mutex_lock(&inkface_dirt_mutex);
    inkface_dirt_count -= count;
    if(inkface_dirt_count < 0) 
        inkface_dirt_count = 0;
    pthread_mutex_unlock(&inkface_dirt_mutex);
}

void
paint(void *arg)
{
    if(!inkface_dirt_count) return;

    GList *elem = sortedElemList;
    while(elem)
    {
        Element *element = (Element *)elem->data;

        ASSERT(element);

        if(element->draw) {
            element->draw(element,ctx);
        } else {
            cairo_set_source_surface(ctx,
                element->surface,element->x,element->y);
            cairo_paint(ctx);
        }

        elem = elem->next;
    }

    #ifdef DOUBLE_BUFFER
    XdbeBeginIdiom(dpy);
    XdbeSwapBuffers(dpy,&swapinfo,1);
    XSync(dpy,0);
    XdbeEndIdiom(dpy);
    #else
    XFlush(dpy);
    #endif

    decr_dirt_count(1);
}

void *
painter_thread(void *arg)
{
    int rc=0;
    struct timespec timeout;
    struct timeval curtime;

    while(1)
    {
        ASSERT(!gettimeofday(&curtime,NULL))
        timeout.tv_sec = curtime.tv_sec;
        timeout.tv_nsec = curtime.tv_usec * 1000;
        timeout.tv_nsec += (REFRESH_INTERVAL_MSEC * 1000000L);
        timeout.tv_sec += timeout.tv_nsec/1000000000L;
        timeout.tv_nsec %= 1000000000L;

        rc=pthread_cond_timedwait(&paint_condition,&paint_mutex,&timeout);

        if(rc!=0){
            if(rc == ETIMEDOUT){
                paint(NULL);
                continue;
            } else {
                printf("<<%s>> pthread_cond_timwait returned %d\n",
                        __FUNCTION__,rc);
                continue;
            }
        }
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

void init_backend(const char* svgfilename,gboolean fullscreen)
{
    ASSERT(svgfilename);

    int status = 0;
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
    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;

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
    ASSERT(screen >= 0);

    atoms_WINDOW_STATE
        = XInternAtom(dpy, "_NET_WM_STATE",False);
    ASSERT((atoms_WINDOW_STATE != BadAlloc && 
            atoms_WINDOW_STATE != BadValue));
    atoms_WINDOW_STATE_FULLSCREEN
        = XInternAtom(dpy, "_NET_WM_STATE_FULLSCREEN",False);
    ASSERT((atoms_WINDOW_STATE_FULLSCREEN != BadAlloc && 
            atoms_WINDOW_STATE_FULLSCREEN != BadValue));

    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    x, y,
                    dim.width, dim.height,
                    0,
                    BlackPixel(dpy,screen),
                    BlackPixel(dpy,screen)));

    if(fullscreen){
        /* Set the wmhints needed for fullscreen */
        status = XChangeProperty(dpy, win, atoms_WINDOW_STATE, XA_ATOM, 32,
                        PropModeReplace,
                        (unsigned char *) &atoms_WINDOW_STATE_FULLSCREEN, 1);
        ASSERT(status != BadAlloc);
        ASSERT(status != BadAtom);
        ASSERT(status != BadMatch);
        ASSERT(status != BadPixmap);
        ASSERT(status != BadValue);
        ASSERT(status != BadWindow);
    }

    #ifdef DOUBLE_BUFFER
    /* Enabled double buffering */
    backBuffer = XdbeAllocateBackBufferName(dpy,win,XdbeBackground);
    swapinfo.swap_window = win;
    swapinfo.swap_action = XdbeBackground;
    #endif

    XClearWindow(dpy,win);
    XMapWindow(dpy, win);

    cairo_surface_t *surface = NULL;
    Visual *visual = DefaultVisual(dpy,DefaultScreen(dpy));
    ASSERT(visual)

    #ifdef DOUBLE_BUFFER
    ASSERT(surface = cairo_xlib_surface_create(
                        dpy, backBuffer, visual, dim.width,dim.height));
    #else
    ASSERT(surface = cairo_xlib_surface_create(
                        dpy, win, visual, dim.width,dim.height));
    #endif 
    ASSERT(ctx = cairo_create(surface));

}

void cleanup_backend()
{
    GList *iter = sortedElemList;
    while(iter){
        Element *el = (Element *)iter->data;

        if(el->cr) cairo_destroy(el->cr);
        if(el->surface) cairo_surface_destroy(el->surface);
        if(el->name) g_free(el->name);
        if(el->on_mouse_over) g_free(el->on_mouse_over);
        g_free(el);
        
        iter = iter->next;
    }
    //g_free(sortedElemList);
    rsvg_term ();

}

GList *
load_element_list()
{
    /*
     * Create Element objects from the loaded SVG
     */

    GList *eidList = inkface_get_element_ids(handle);
    ASSERT(eidList);

    GList *head_eidList = eidList;

    GList *elemList = NULL;
    Element *element = NULL;

    while(eidList){

        ASSERT(eidList->data);

        element = (Element *)g_malloc(sizeof(Element));
        memset(element,0,sizeof(Element));
        strncpy(element->id,eidList->data,31);  //TODO macro

        inkface_get_element(handle,element,FALSE);

        elemList = g_list_prepend(elemList,element);

        g_free(eidList->data);
        eidList = eidList->next;
    }
    g_list_free(head_eidList);

    ASSERT(sortedElemList = g_list_sort(elemList,compare_element));

    return sortedElemList;
}

void
sort_elements()
{
    /* TODO this can potentially lead to race conditions
     * It's is necessary to lock the sortedElementList, else 
     * the concurrent operations which are in the middle of iterating
     * over the list will get confused
     */
    ASSERT(sortedElemList = g_list_sort(sortedElemList,compare_element));
}

void 
fork_painter_thread()
{
    /*
     * Fork a thread to draw the sorted element list
     */
    pthread_mutex_init(&inkface_dirt_mutex,NULL);
    pthread_t thr;
    pthread_create(&thr,NULL,painter_thread,NULL);

}

