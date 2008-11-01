
#include "rsvg.h"
#include "macro.h"

#include "errno.h"
#include "string.h"
#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "common.h"
#include "inkface.h"

//--------------
// canvas
//--------------

static void 
canvas_init(
    canvas_t *self,
    int width, int height, 
    int fullscreen,
    paintfunc_t paint,
    void *paint_arg)
{
    int status = 0;
    Window rwin;
    int x=0, y=0;
    int screen = 0;

    ASSERT(self);
    self->width = width;
    self->height = height;
    self->fullscreen = fullscreen;
    self->paint = paint;
    self->paint_arg = paint_arg;

    XInitThreads();

    ASSERT(self->dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(self->dpy));
    screen = DefaultScreen(self->dpy);
    ASSERT(screen >= 0);

    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;
    atoms_WINDOW_STATE
        = XInternAtom(self->dpy, "_NET_WM_STATE",False);
    ASSERT((atoms_WINDOW_STATE != BadAlloc && 
            atoms_WINDOW_STATE != BadValue));
    atoms_WINDOW_STATE_FULLSCREEN
        = XInternAtom(self->dpy, "_NET_WM_STATE_FULLSCREEN",False);
    ASSERT((atoms_WINDOW_STATE_FULLSCREEN != BadAlloc && 
            atoms_WINDOW_STATE_FULLSCREEN != BadValue));

    ASSERT(self->win = XCreateSimpleWindow(
                    self->dpy,
                    rwin,
                    x, y,
                    self->width, self->height,
                    0,
                    BlackPixel(self->dpy,screen),
                    BlackPixel(self->dpy,screen)));

    if(self->fullscreen){  
        /* Set the wmhints needed for fullscreen */
        status = XChangeProperty(self->dpy, self->win, 
                        atoms_WINDOW_STATE, XA_ATOM, 32,
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
    self->backBuffer = XdbeAllocateBackBufferName(self->dpy,self->win,XdbeBackground);
    self->swapinfo.swap_window = self->win;
    self->swapinfo.swap_action = XdbeBackground;
    #endif

    XClearWindow(self->dpy,self->win);

    self->surface = NULL;
    Visual *visual = DefaultVisual(self->dpy,DefaultScreen(self->dpy));
    ASSERT(visual)

    #ifdef DOUBLE_BUFFER
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->backBuffer, visual, self->width, self->height));
    #else
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->win, visual, self->width, self->height));
    #endif 
    ASSERT(self->ctx = cairo_create(self->surface));

    ASSERT(!pthread_mutex_init(&(self->dirt_mutex),NULL));


    // Fork a painter thread which does refresh jobs
    ASSERT(!pthread_mutex_init(&(self->paint_mutex),NULL));
    ASSERT(!pthread_cond_init(&(self->paint_condition),NULL));
    ASSERT(!pthread_create(&(self->painter_thr),NULL,painter_thread,self));

}

void canvas_show(canvas_t *self)
{
    // Map the window so that it's visible
    XMapWindow(self->dpy, self->win);
    XFlush(self->dpy);
    self->inc_dirt_count(self,1);
}

void canvas_refresh(canvas_t *self)
{

}
                    
void canvas_cleanup(canvas_t *self)
{
    rsvg_term();

    self->shutting_down = TRUE;

    // Let's wait for the painter_thread to exit
    // before we destroy the X cairo surface on which it
    // might be drawing
    //
    ASSERT(!pthread_join(self->painter_thr,NULL));
    
    ASSERT(!pthread_mutex_destroy(&(self->paint_mutex)));
    ASSERT(!pthread_cond_destroy(&(self->paint_condition)));

    #ifdef DOUBLE_BUFFER
    XdbeDeallocateBackBufferName(self->dpy,self->backBuffer);
    #endif
    XUnmapWindow(self->dpy,self->win);
    XDestroyWindow(self->dpy,self->win);
    XCloseDisplay(self->dpy);

}

void inc_dirt_count(canvas_t *self, int count)
{
    CHK_ERRNO(pthread_mutex_lock(&(self->dirt_mutex)));
    self->dirt_count += count;
    CHK_ERRNO(pthread_mutex_unlock(&(self->dirt_mutex)));
}

void dec_dirt_count(canvas_t *self, int count)
{
    CHK_ERRNO(pthread_mutex_lock(&(self->dirt_mutex)));
    self->dirt_count -= count;
    if(self->dirt_count < 0) {
        self->dirt_count = 0;
    }
    CHK_ERRNO(pthread_mutex_unlock(&(self->dirt_mutex)));
}


canvas_t *canvas_new(void)
{
    canvas_t *object = NULL;
    ASSERT(object = (canvas_t *)malloc(sizeof(canvas_t)));
    memset(object,0,sizeof(canvas_t));
    object->init = canvas_init;
    object->cleanup = canvas_cleanup;
    object->refresh = canvas_refresh;
    object->show = canvas_show;
    object->inc_dirt_count = inc_dirt_count;
    object->dec_dirt_count = dec_dirt_count;
    return object;
}


//--------------------
// Element
//--------------------

//
// Ideally there should be an element_t class here in the cobject layer,
// just like the canvas_t above.
//
// However a bulk of Element is defined inside libaltsvg. So defining a
// new object just for the sake of it seems superfluous. Instead this part
// will contain element related methods that do not fit inside libaltsvg
// and yet are common across all bindings.
//
// If this collection of element related generic methods grows big enough
// to justify a class in cobject layer then we can go for it.
// 

int process_motion_event(Element *el,XMotionEvent *mevent)
{
    ASSERT(el);
    ASSERT(mevent);

    int state = 0x0;
    int nowInFocus = FALSE;

    if((mevent->x > el->x) &&
        (mevent->y > el->y) &&
        (mevent->x < (el->x+el->w)) &&
        (mevent->y < (el->y+el->h)))
    {
        nowInFocus = TRUE;
        state |= POINTER_STATE_TAP;
    }

    if(el->inFocus && !nowInFocus){
        state |= POINTER_STATE_LEAVE;
    }

    if(!el->inFocus && nowInFocus){
        state |= POINTER_STATE_ENTER;
    }
 
    el->inFocus = nowInFocus;

    return state; 
}

//--------------------
// Helper functions
//--------------------

void *painter_thread(void *arg)
{
    int rc=0;
    struct timespec timeout;
    struct timeval curtime;

    canvas_t *canvas = (canvas_t *)arg;
    ASSERT(canvas);

    while(1)
    {
        ASSERT(!gettimeofday(&curtime,NULL))
        timeout.tv_sec = curtime.tv_sec;
        timeout.tv_nsec = curtime.tv_usec * 1000;
        timeout.tv_nsec += (REFRESH_INTERVAL_MSEC * 1000000L);
        timeout.tv_sec += timeout.tv_nsec/1000000000L;
        timeout.tv_nsec %= 1000000000L;

        ASSERT(!pthread_mutex_lock(&(canvas->paint_mutex)));
        rc=pthread_cond_timedwait(
                    &(canvas->paint_condition),
                    &(canvas->paint_mutex),
                    &timeout);
        ASSERT(!pthread_mutex_unlock(&(canvas->paint_mutex)));

        if(canvas->shutting_down){
            pthread_exit(NULL);
        }

        if(rc!=0){
            if(rc == ETIMEDOUT){
                if(canvas->paint) {
                    canvas->paint(canvas->paint_arg);
                }
            } else {
                LOG("pthread_cond_timwait returned %d\n",rc);
            }
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

GList *
load_element_list(RsvgHandle *handle)
{
    /*
     * Create Element objects from the loaded SVG
     */

    ASSERT(handle);
    GList *sorted_elist = NULL;
    GList *eidlist = inkface_get_element_ids(handle);
    ASSERT(eidlist);

    GList *head_eidlist = eidlist;

    GList *elist = NULL;
    Element *e = NULL;

    while(eidlist){

        ASSERT(eidlist->data);

        e = (Element *)g_malloc(sizeof(Element));
        memset(e,0,sizeof(Element));
        strncpy(e->id,eidlist->data,31);  //TODO macro

        inkface_get_element(handle,e,FALSE);

        elist = g_list_prepend(elist,e);

        g_free(eidlist->data);
        eidlist = eidlist->next;
    }
    g_list_free(head_eidlist);

    ASSERT(sorted_elist = g_list_sort(elist,compare_element));

    return sorted_elist;
}

RsvgHandle *
rsvg_handle_from_file(const char *filename)
{
    GByteArray *bytes = NULL;
    RsvgHandle *handle = NULL;
    guchar buffer[4096];
    FILE *f;
    int length;

    ASSERT(filename);
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

