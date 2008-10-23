
#include "Python.h"
#include "structmember.h"

#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xdbe.h>

#include "inkface.h"

#define DOUBLE_BUFFER
#define REFRESH_INTERVAL_MSEC 50

#include "common.h"

void *painter_thread(void *arg);

RsvgHandle *handle = NULL;

int shutting_down = FALSE;
void cleanup();
pthread_t painter_thr;

/*
 * "canvas" type object
 */

//TODO: Make canvas singleton

typedef struct {
    PyObject_HEAD
    int width;
    int height;
    PyObject *fullscreen;
    Display *dpy; 
    cairo_t *ctx;
    cairo_surface_t *surface;
    Window win;
    PyObject *element_list;

    // Painting control members
    int dirt_count;
    unsigned int timer_step;
    int timer_counter;
    pthread_mutex_t paint_mutex;
    pthread_cond_t paint_condition;
    pthread_mutex_t dirt_mutex;

    PyObject *onTimer;

    #ifdef DOUBLE_BUFFER
    XdbeBackBuffer backBuffer;
    XdbeSwapInfo swapinfo;
    #endif
} Canvas_t;

/*
 * "element" type object
 */
typedef struct {
    PyObject_HEAD
    cairo_surface_t *surface;
} PycairoSurface_t;

typedef struct {
    PyObject_HEAD

    int x;
    int y;
    int w;
    int h;
    int order;
    int inFocus;

    PyObject *name;
    PyObject *id;
    PyObject *text;

    int opacity;

    PycairoSurface_t *pysurface;    

    // private 
    Element *element;

    // Callback handlers
    PyObject *onDraw;
    PyObject *onTap;
    PyObject *onMouseEnter;
    PyObject *onMouseLeave;

} Element_t;

void draw(Canvas_t *canvas, Element_t *element);
void inc_dirt_count(Canvas_t *canvas, int count);
void dec_dirt_count(Canvas_t *canvas, int count);

//
// "canvas" object methods and members
//

static PyObject *
canvas_new (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    // Unused - GenericNew() is enough so far
}

static int
canvas_init(Canvas_t *self, PyObject *args, PyObject *kwds)
{
    int status = 0;
    Window rwin;
    int screen = 0;
    int x=0, y=0;
    int xsp_event_base=-1;
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;

    // Parse keyword args

    #define DEFAULT_WIDTH 800
    #define DEFAULT_HEIGHT 480 
    self->width=0; 
    self->height=0;
    self->fullscreen = Py_False;
    self->timer_step = 0;
    self->timer_counter = 0;
    self->onTimer = NULL;
    static char *kwlist[] = {"width", "height", "fullscreen", NULL};

    ASSERT(PyArg_ParseTupleAndKeywords(args, kwds, "|iiO", kwlist, 
                  &(self->width), &(self->height), &(self->fullscreen)))

    if(self->width <= 0) self->width = DEFAULT_WIDTH;
    if(self->height <= 0) self->height = DEFAULT_HEIGHT;

    //
    // Fullscreen preferences:
    //
    // 1. env var INKFACE_FULLSCREEN 
    // 2. kwd arg fullscreen 
    //
    char *env_fullscreen = getenv("INKFACE_FULLSCREEN");
    if(env_fullscreen && !strncmp(env_fullscreen,"TRUE",4)){
        self->fullscreen = Py_True;
    } else {
        if((self->fullscreen == NULL) || (!PyBool_Check(self->fullscreen))) {
            self->fullscreen = Py_False;
        } else {
            if(self->fullscreen == Py_True){
                self->fullscreen = Py_True;
            } else {
                self->fullscreen = Py_False;
            }
        }
    }

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

    if(self->fullscreen == Py_True){  
        /* Set the wmhints needed for fullscreen */
        status = XChangeProperty(self->dpy, self->win, atoms_WINDOW_STATE, XA_ATOM, 32,
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

    // Initialize the active element list
    self->element_list = PyList_New(0);

    // Initialize multi thread support for Python interpreter
    PyEval_InitThreads();

    // Fork a painter thread which does refresh jobs
    pthread_mutex_init(&(self->dirt_mutex),NULL);
    pthread_create(&painter_thr,NULL,painter_thread,self);

    return 0;
}

static PyObject*
canvas_cleanup(Canvas_t *self, PyObject *args)
{
    shutting_down = TRUE;

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject*
canvas_draw(Canvas_t *self, PyObject *args)
{
    Element_t *element;

    if(!PyArg_ParseTuple(args,"O",&element)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!element){
        Py_INCREF(Py_None);
        return Py_None;
    }

    draw(self,element);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
canvas_show(Canvas_t *self, PyObject *args)
{
    XMapWindow(self->dpy, self->win);
    
    XFlush(self->dpy);

    inc_dirt_count(self,1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
canvas_refresh(Canvas_t *self, PyObject *args)
{
    inc_dirt_count(self,1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
canvas_set_timer(Canvas_t *canvas, PyObject *args)
{
    int interval = -1;
    PyObject *onTimer_pyo;
    if(!PyArg_ParseTuple(args,"iO",&interval,&onTimer_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(interval < 0){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid timer interval");
        return NULL;
    }

    ASSERT(onTimer_pyo);
    canvas->onTimer = onTimer_pyo;

    canvas->timer_step = (unsigned int)(interval/REFRESH_INTERVAL_MSEC);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
canvas_register_elements(PyObject *self, PyObject *args)
{
    PyObject *elemList_pyo;

    if(!PyArg_ParseTuple(args,"O",&elemList_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!elemList_pyo){
        Py_INCREF(Py_None);
        return Py_None;
    }

    ASSERT(PyList_Check(elemList_pyo));

    PyObject *iterator = PyObject_GetIter(elemList_pyo);
    PyObject *item;

    ASSERT(iterator);

    while(item = PyIter_Next(iterator)){
        PyList_Append(((Canvas_t *)self)->element_list,item);
    }

    Py_DECREF(iterator);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
canvas_unregister_elements(Canvas_t *self, PyObject *args)
{
    PyObject *elemList_pyo;

    if(!PyArg_ParseTuple(args,"O",&elemList_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!elemList_pyo){
        Py_INCREF(Py_None);
        return Py_None;
    }

    ASSERT(PyList_Check(elemList_pyo));

    //TODO:
    
    #if 0
    PyObject *iterator = PyObject_GetIter(elemList_pyo);
    PyObject *item;

    ASSERT(iterator);

    while(item = PyIter_Next(iterator)){
        PyObject *reg_iterator = PyObject_GetIter(self->element_list);
        PyObject *reg_item;
        ASSERT(reg_iterator);

        while(reg_item == PyIter_Next(reg_iterator)){
             
        }

        Py_DECREF(item);
    }
    #endif

    Py_INCREF(Py_None);
    return Py_None;
}

// Private method of canvas
void cleanup(Canvas_t *self)
{
    rsvg_term();

    // Let's wait for the painter_thread to exit
    // before we destroy the X cairo surface on which it
    // might be drawing
    //
    Py_BEGIN_ALLOW_THREADS
    pthread_join(painter_thr,NULL);
    Py_END_ALLOW_THREADS

    #ifdef DOUBLE_BUFFER
    XdbeDeallocateBackBufferName(self->dpy,self->backBuffer);
    #endif
    XUnmapWindow(self->dpy,self->win);
    XDestroyWindow(self->dpy,self->win);
    XCloseDisplay(self->dpy);
}

static PyObject*
canvas_eventloop(Canvas_t *self, PyObject *args)
{
    Canvas_t *canvas = (Canvas_t *)self;
    /*
     * Setup the event listening
     */
    XSelectInput(canvas->dpy, canvas->win, 
                            StructureNotifyMask|PointerMotionMask);
    while(1)
    {
        XMotionEvent *mevent;
        XEvent event;

        Py_BEGIN_ALLOW_THREADS

        XNextEvent(canvas->dpy,&event);

        Py_END_ALLOW_THREADS
        
        switch(event.type){
        case MapNotify:
            break;
        case MotionNotify:
            mevent = (XMotionEvent *)(&event);
            /*
             * Trigger the events in decreasing "order" of the elements
             */
            PyObject *iterator = PyObject_GetIter(self->element_list);
            PyObject *item;
            while(item = PyIter_Next(iterator)){

                gboolean nowInFocus = FALSE;

                Element_t *el = (Element_t *)item;

                if((mevent->x > el->x) &&
                    (mevent->y > el->y) &&
                    (mevent->x < (el->x+el->w)) &&
                    (mevent->y < (el->y+el->h)))
                {
                    nowInFocus = TRUE;
                    if(PyCallable_Check(el->onTap)) {
                        PyObject_CallFunction(el->onTap,
                            "OO",el,self->element_list);
                    }
                } 

                if(el->inFocus && !nowInFocus){
                    if(PyCallable_Check(el->onMouseLeave)) {
                        PyObject_CallFunction(el->onMouseLeave,
                            "OO",el,self->element_list);
                    }
                }

                if(!el->inFocus && nowInFocus){
                    if(PyCallable_Check(el->onMouseEnter)) {
                        PyObject_CallFunction(el->onMouseEnter,
                            "OO",el,self->element_list);
                    }
                }

                el->inFocus = nowInFocus;

                Py_DECREF(item);
            }

            Py_DECREF(iterator);

            break;
        case DestroyNotify:
            // canvas is destroyed get out of eventloop
            return;    
        default:
            break;
        }

        // Check if shutting_down was set during above event processing
        if(shutting_down){
            cleanup(self);
            return;
        }
    }

}


static PyMethodDef canvas_methods[] = {
    { "register_elements", (PyCFunction)canvas_register_elements, 
        METH_VARARGS, "Register elements with canvas" },
    { "unregister_elements", (PyCFunction)canvas_unregister_elements, 
        METH_VARARGS, "Unregister elements from canvas" },
    { "eventloop", (PyCFunction)canvas_eventloop, 
        METH_NOARGS, "Make canvas process events in infinite loop" },
    { "draw", (PyCFunction)canvas_draw, 
        METH_VARARGS, "Draw the element canvas" },
    { "set_timer", (PyCFunction)canvas_set_timer, 
        METH_VARARGS, 
        "Set a timer which expires periodically and triggers canvas refresh" },
    { "show", (PyCFunction)canvas_show, 
        METH_NOARGS, "Show the canvas" },
    { "refresh", (PyCFunction)canvas_refresh, 
        METH_NOARGS, "Refresh the canvas" },
    { "cleanup", (PyCFunction)canvas_cleanup, 
        METH_NOARGS, "Cleanup the canvas" },
    {NULL, NULL, 0, NULL},
};

static PyMemberDef canvas_members[] = {
    { "width", T_INT, offsetof(Canvas_t,width),0,"Width of Canvas"},
    { "height", T_INT, offsetof(Canvas_t,height),0,"Height of Canvas"},
    { "timer_step", T_INT, offsetof(Canvas_t,timer_step),0,"Timer step"},
    { "fullscreen", T_OBJECT, offsetof(Canvas_t,fullscreen),0,
        "Fullscreen flag"},
    { "elements", T_OBJECT, offsetof(Canvas_t,element_list),0,
            "Elements currently registered with Canvas"},
    { NULL }
};


PyTypeObject Canvas_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "inkface.canvas",                   /* tp_name */
    sizeof(Canvas_t),                   /* tp_basicsize */
    0,                                  /* tp_itemsize */
    0,                                  /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE, /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    canvas_methods,                     /* tp_methods */
    canvas_members,                     /* tp_members */
    0,                                  /* tp_getset */
    0, /* &Canvas_Type, */              /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)canvas_init,              /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)canvas_new,                /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};

//
// "element" object methods and members
//


static int
element_init(Element_t *self, PyObject *args, PyObject *kwds)
{
    Py_INCREF(Py_None);
    self->text = Py_None;

    Py_INCREF(Py_None);
    self->onTap = Py_None;
    Py_INCREF(Py_None);
    self->onMouseEnter = Py_None;
    Py_INCREF(Py_None);
    self->onMouseLeave = Py_None;
    Py_INCREF(Py_None);
    self->onDraw = Py_None;

    return 0;
}

static PyObject*
element_test(Element_t *self, PyObject *args)
{
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
element_refresh(Element_t *self,PyObject *args)
{
    g_string_free(self->element->text,TRUE);
    self->element->text = g_string_new(
        PyString_AsString(self->text));
    inkface_get_element(handle,self->element,TRUE);

    free(self->pysurface);
    ASSERT(self->pysurface = (PycairoSurface_t *)
        malloc(sizeof(PycairoSurface_t)));
    self->pysurface->surface = self->element->surface;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
element_richcompare(Element_t *v, Element_t *w, int op)
{
    int r;
    ASSERT(v)
    ASSERT(w)
    int vo = v->order;
    int wo = w->order;
    switch (op) {
    case Py_EQ:
        r = vo == wo;
        break;
    case Py_NE:
        r = vo != wo;
        break;
    case Py_LE:
        r = vo <= wo;
        break;
    case Py_GE:
        r = vo >= wo;
        break;
    case Py_LT:
        r = vo < wo;
        break;
    case Py_GT:
        r = vo > wo;
        break;
    }

    return PyBool_FromLong(r);
}

static PyMethodDef element_methods[] = {
    { "test", 
        (PyCFunction)element_test, 
        METH_NOARGS, "Test" },
    { "refresh", 
        (PyCFunction)element_refresh, 
        METH_NOARGS, "Refresh/Reload the element" },
    { NULL, NULL, 0, NULL },
};

static PyMemberDef element_members[] = {
    { "x", T_INT, offsetof(Element_t,x),0,"x coord"},
    { "y", T_INT, offsetof(Element_t,y),0,"y coord"},
    { "w", T_INT, offsetof(Element_t,w),0,"width"},
    { "h", T_INT, offsetof(Element_t,h),0,"height"},
    { "order", T_INT, offsetof(Element_t,order),0,"order to draw"},
    { "name", T_OBJECT,offsetof(Element_t,name),0,"Name of the element"},
    { "id", T_OBJECT,offsetof(Element_t,id),0,"Id of the element"},
    { "text", T_OBJECT,offsetof(Element_t,text),0,"Text of a text element"},
    { "opacity", T_INT, offsetof(Element_t,opacity),0,"Opacity of element"},
    { "onDraw", T_OBJECT,offsetof(Element_t,onDraw),0,"Draw handler"},
    { "onTap", T_OBJECT,offsetof(Element_t,onTap),0,"Tap handler"},
    { "onMouseEnter", T_OBJECT,offsetof(Element_t,onMouseEnter),0,
                    "Mouse Enter handler"},
    { "onMouseLeave", T_OBJECT,offsetof(Element_t,onMouseLeave),0,
                    "Mouse Leave handler"},
    { NULL }
};

static PyObject *
element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element_t *self;

    self = (Element_t *)type->tp_alloc(type,0);

    if(self){
        self->pysurface = (PycairoSurface_t *)
            malloc(sizeof(PycairoSurface_t));
    }

    return (PyObject *)self;
}

static void
element_dealloc(Element_t *self)
{
    if (self->name) Py_DECREF(self->name);
    if (self->id) Py_DECREF(self->id);
    if (self->text) Py_DECREF(self->text);

    if (self->onDraw) Py_DECREF(self->onDraw);
    if (self->onTap) Py_DECREF(self->onTap);
    if (self->onMouseEnter) Py_DECREF(self->onMouseEnter);
    if (self->onMouseLeave) Py_DECREF(self->onMouseLeave);

    // Element cleanup : TODO move to libaltsvg
    if(self->element) {
        if(self->element->cr) {
            cairo_destroy(self->element->cr);
        }
        if(self->element->surface){
            cairo_surface_destroy(self->element->surface);
        }
        if(self->element->name) {
            free(self->element->name);
        }
        if(self->element->text){
            g_string_free(self->element->text,TRUE);
        }
    
        free(self->element);
    }

    // Don't have to cairo_destroy_surface, because that must have
    // been already cleared during element's cleanup
    if(self->pysurface){
        free(self->pysurface);
    }

    self->ob_type->tp_free((PyObject *)self);
}

PyTypeObject Element_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "inkface.element",                  /* tp_name */
    sizeof(Element_t),                  /* tp_basicsize */
    0,                                  /* tp_itemsize */
    element_dealloc,                    /* tp_dealloc */
    0,                                  /* tp_print */
    0,                                  /* tp_getattr */
    0,                                  /* tp_setattr */
    0,                                  /* tp_compare */
    0,                                  /* tp_repr */
    0,                                  /* tp_as_number */
    0,                                  /* tp_as_sequence */
    0,                                  /* tp_as_mapping */
    0,                                  /* tp_hash */
    0,                                  /* tp_call */
    0,                                  /* tp_str */
    0,                                  /* tp_getattro */
    0,                                  /* tp_setattro */
    0,                                  /* tp_as_buffer */
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,  /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    element_richcompare,                /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    element_methods,                    /* tp_methods */
    element_members,                    /* tp_members */
    0,                                  /* tp_getset */
    0, /* &Element_Type, */             /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)element_new,               /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};



/*
 * "inkface" module
 */
static PyObject*
loadsvg(PyObject *self, PyObject *args)
{
    char *svgname;
    ASSERT(PyArg_ParseTuple(args,"s",&svgname))
        
    ASSERT(svgname)

    // Create rsvg handle for the SVG file
    ASSERT(handle = rsvg_handle_from_file(svgname));
 
    // Get list of element IDs in the SVG
    GList *eidList = inkface_get_element_ids(handle);
    ASSERT(eidList);

    GList *head_eidList = eidList;

    Element *element = NULL;

    PyObject *pyElementList = PyList_New(0);

    while(eidList){

        ASSERT(eidList->data);

        element = (Element *)g_malloc(sizeof(Element));
        memset(element,0,sizeof(Element));

        // Find element for the id
        strncpy(element->id,eidList->data,31);  //TODO macro
        inkface_get_element(handle,element,0);

        // Create python object for Element
        PyTypeObject *pytype = NULL;
        Element_t *pyo;
        pytype = &Element_Type;
        ASSERT(pyo = pytype->tp_alloc(pytype,0));

        pyo->x = element->x;
        pyo->y = element->y;
        pyo->w = element->w;
        pyo->h = element->h;
        pyo->order = element->order;
        pyo->name = PyString_FromString(element->name);
        pyo->id = PyString_FromString(element->id);
        if(element->text){
            pyo->text = PyString_FromString(element->text->str);
        }
        ASSERT(pyo->pysurface = (PycairoSurface_t *)
            malloc(sizeof(PycairoSurface_t)));
        pyo->pysurface->surface = element->surface;

        pyo->element = element;

        // Add python object to list
        PyList_Append(pyElementList,(PyObject *)pyo);

        // Free id and jump to next
        g_free(eidList->data);
        eidList = eidList->next;
    }
    g_list_free(head_eidList);

    ASSERT(!PyList_Sort(pyElementList));

    return pyElementList;

}

static PyMethodDef inkface_methods[] =
{
    { "loadsvg", (PyCFunction)loadsvg, METH_VARARGS, NULL },
    { NULL, NULL, 0, NULL},
};

DL_EXPORT(void)
initinkface(void)
{
    PyObject *m;

    rsvg_init();

    Canvas_Type.tp_new = PyType_GenericNew;

    if (PyType_Ready(&Element_Type) < 0) return;
    if (PyType_Ready(&Canvas_Type) < 0) return;

    m = Py_InitModule("inkface",inkface_methods);

    PyModule_AddObject(m,"canvas",(PyObject *)&Canvas_Type);

}

/* INTERNAL FUNCTIONS */
/* Thread-safe routines to manipulate paint_mutex */
void inc_dirt_count(Canvas_t *canvas, int count)
{
    pthread_mutex_lock(&(canvas->dirt_mutex));
    canvas->dirt_count += count;
    pthread_mutex_unlock(&(canvas->dirt_mutex));
}

void dec_dirt_count(Canvas_t *canvas, int count)
{
    pthread_mutex_lock(&(canvas->dirt_mutex));
    canvas->dirt_count -= count;
    if(canvas->dirt_count < 0) 
        canvas->dirt_count = 0;
    pthread_mutex_unlock(&(canvas->dirt_mutex));
}

void
paint(void *arg)
{
    Canvas_t *canvas = (Canvas_t *) arg;

    if(canvas->timer_step){
        canvas->timer_counter++;
        canvas->timer_counter = canvas->timer_counter % canvas->timer_step;
    }

    if((canvas->timer_counter == 0) || (canvas->dirt_count))
    {

        // BEGIN - Python thread safety code block
        PyGILState_STATE gstate;
        gstate = PyGILState_Ensure();
    
        if(canvas->timer_counter == 0){
            if(canvas->onTimer && PyCallable_Check(canvas->onTimer)){
                PyObject_CallFunction(canvas->onTimer,NULL);
            }
        }
        
        PyObject *iterator = PyObject_GetIter(canvas->element_list);
        PyObject *item;
        while(item = PyIter_Next(iterator)){
            Element_t *el = (Element_t *)item;
    
            if(PyCallable_Check(el->onDraw)){
                // Call element's custom draw handler
                PyObject_CallFunction(el->onDraw,"O",el);
            } else {
                // Call canvas's default draw method
                draw(canvas,el);
            }
    
            Py_DECREF(item);
        }
        Py_DECREF(iterator);
    
        PyGILState_Release(gstate);
        // END - Python thread safety code block
    
        #ifdef DOUBLE_BUFFER
        XdbeBeginIdiom(canvas->dpy);
        XdbeSwapBuffers(canvas->dpy,&canvas->swapinfo,1);
        XSync(canvas->dpy,0);
        XdbeEndIdiom(canvas->dpy);
        #else
        XFlush(canvas->dpy);
        #endif

        dec_dirt_count(canvas,1);

    }
}

void *
painter_thread(void *arg)
{
    int rc=0;
    struct timespec timeout;
    struct timeval curtime;

    Canvas_t *canvas = (Canvas_t *)arg;

    while(1)
    {
        ASSERT(!gettimeofday(&curtime,NULL))
        timeout.tv_sec = curtime.tv_sec;
        timeout.tv_nsec = curtime.tv_usec * 1000;
        timeout.tv_nsec += (REFRESH_INTERVAL_MSEC * 1000000L);
        timeout.tv_sec += timeout.tv_nsec/1000000000L;
        timeout.tv_nsec %= 1000000000L;

        rc=pthread_cond_timedwait(
                    &(canvas->paint_condition),
                    &(canvas->paint_mutex),
                    &timeout);

        if(shutting_down){
            pthread_exit(NULL);
        }

        if(rc!=0){
            if(rc == ETIMEDOUT){
                paint(canvas);
                continue;
            } else {
                LOG("pthread_cond_timwait returned %d\n",rc);
                continue;
            }
        }
    }
}

void 
draw(Canvas_t *canvas, Element_t *element)
{
    cairo_set_source_surface(canvas->ctx,
        element->pysurface->surface,element->x,element->y);
    cairo_paint(canvas->ctx);
}
