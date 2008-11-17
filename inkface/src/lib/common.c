
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
#include "canvas-x.h"

#ifdef HAS_XSP
#include <X11/extensions/Xsp.h>
int xsp_event_base=-1;
#endif // HAS_XSP


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

    static int tap_counter = 0;
    int state = 0x0;
    int nowInFocus = FALSE;

    if((mevent->x > el->x) &&
        (mevent->y > el->y) &&
        (mevent->x < (el->x+el->w)) &&
        (mevent->y < (el->y+el->h)))
    {
        nowInFocus = TRUE;
    }

    if(el->inFocus && !nowInFocus){
        state |= POINTER_STATE_LEAVE;
    }

    if(!el->inFocus && nowInFocus){
        state |= POINTER_STATE_ENTER;
    }
 
    if(nowInFocus){
        if(!tap_counter) { 
            state |= POINTER_STATE_TAP;
        }
        tap_counter = (tap_counter + 1)%DUP_TAP_IGNORANCE_LIMIT;
    }
    el->inFocus = nowInFocus;

    return state; 
}

int calculate_pressure(Element *el, XEvent *event)
{
#ifdef HAS_XSP
    int tx=0,ty=0,pressure=0;
    XSPRawTouchscreenEvent xsp_event;

    if(event->type == xsp_event_base)
    {
        memcpy(&xsp_event, event,
            sizeof(XSPRawTouchscreenEvent));
        tx = xsp_event.x;
        ty = xsp_event.y;
        pressure = xsp_event.pressure;
    
        /* translate raw coordinates */
        TRANSLATE_RAW_COORDS(&tx, &ty);
        
        if((tx > el->x) && (ty > el->y) &&
            (tx < el->x+el->w) && (ty < el->y+el->h))
        {
            return pressure;
        }
    }
#endif
    return 0;
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
load_element_list(char *svgname)
{
    ASSERT(svgname);

    RsvgHandle *handle = NULL;

    // Create rsvg handle for the SVG file
    ASSERT(handle = rsvg_handle_from_file(svgname));
 
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

        e->handle = handle;

        strncpy(e->id,eidlist->data,31);  //TODO macro

        inkface_get_element(e,FALSE);

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

