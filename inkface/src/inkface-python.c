
#include "Python.h"
#include "structmember.h"

#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xdbe.h>

#include "inkface.h"

#define DOUBLE_BUFFER
#define REFRESH_INTERVAL_MSEC 80

RsvgHandle *rsvg_handle_from_file(const char *filename);

/*
 * "canvas" type object
 */

typedef struct {
    PyObject_HEAD
    int width;
    int height;
    Display *dpy; 
    cairo_t *ctx;
    cairo_surface_t *surface;
    Window win;
    PyObject *element_list;

    // Painting control members
    int dirt_count;
    pthread_mutex_t paint_mutex;
    pthread_cond_t paint_condition;

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

    int opacity;

    PycairoSurface_t *surface;    

    // Callback handlers
    PyObject *onTap;
    PyObject *onMouseEnter;
    PyObject *onMouseLeave;
    PyObject *draw;

} Element_t;




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
    Pixmap pix;
    XGCValues gcv;
    GC gc;
    int xsp_event_base=-1;
    int xsp_error_base=-1;
    int xsp_major=-1;
    int xsp_minor=-1;
    Atom atoms_WINDOW_STATE;
    Atom atoms_WINDOW_STATE_FULLSCREEN;

    // Parse keyword args

    #define DEFAULT_WIDTH 800
    #define DEFAULT_HEIGHT 480 
    int width=0, height=0;
    int fullscreen;
    PyObject *fullscreen_pyo = NULL;
    static char *kwlist[] = {"width", "height", "fullscreen", NULL};

    ASSERT(PyArg_ParseTupleAndKeywords(args, kwds, "|iiO", kwlist, 
                                          &width, &height, &fullscreen_pyo))

    if(width <= 0) width = DEFAULT_WIDTH;
    if(height <= 0) height = DEFAULT_HEIGHT;

    if((fullscreen_pyo == NULL) || (!PyBool_Check(fullscreen_pyo))) {
        fullscreen = FALSE;
    } else {
        if(fullscreen_pyo == Py_True){
            fullscreen = TRUE;
        } else {
            fullscreen = FALSE;
        }
    }

    

    XInitThreads();

    ASSERT(self->dpy = XOpenDisplay(0));

    ASSERT(rwin = DefaultRootWindow(self->dpy));
    screen = DefaultScreen(self->dpy);
    ASSERT(screen >= 0);

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
                    width, height,
                    0,
                    BlackPixel(self->dpy,screen),
                    BlackPixel(self->dpy,screen)));

    if(fullscreen){  
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
    //TODO: XMapWindow(self->dpy, self->win);

    self->surface = NULL;
    Visual *visual = DefaultVisual(self->dpy,DefaultScreen(self->dpy));
    ASSERT(visual)

    #ifdef DOUBLE_BUFFER
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->backBuffer, visual, width, height));
    #else
    ASSERT(self->surface = cairo_xlib_surface_create(
                        self->dpy, self->win, visual, width, height));
    #endif 
    ASSERT(self->ctx = cairo_create(self->surface));

    // Initialize the active element list
    self->element_list = PyList_New(0);

    return 0;
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

static PyObject*
canvas_eventloop(Canvas_t *self, PyObject *args)
{
    Canvas_t *canvas = (Canvas_t *)self;
    /*
     * Setup the event listening
     */
    XSelectInput(canvas->dpy, canvas->win, StructureNotifyMask);
    XSelectInput(canvas->dpy, canvas->win, 
                            StructureNotifyMask|PointerMotionMask);
    while(1)
    {
        XMotionEvent *mevent;
        XEvent event;
        XNextEvent(canvas->dpy,&event);
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
                } 

                if(el->inFocus && !nowInFocus){
                    if(PyCallable_Check(el->onMouseLeave)) {
                        PyEval_CallFunction(el->onMouseLeave,
                            "OO",el,self->element_list);
                    }
                }

                if(!el->inFocus && nowInFocus){
                    if(PyCallable_Check(el->onMouseEnter)) {
                        PyEval_CallFunction(el->onMouseEnter,
                            "OO",el,self->element_list);
                    }
                }

                el->inFocus = nowInFocus;

                Py_DECREF(item);
            }

            Py_DECREF(iterator);

            break;
        default:
            break;
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
    {NULL, NULL, 0, NULL},
};

static PyMemberDef canvas_members[] = {
    { "width", T_INT, offsetof(Canvas_t,width),0,"Width of Canvas"},
    { "height", T_INT, offsetof(Canvas_t,height),0,"Height of Canvas"},
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
    self->onTap = Py_None;
    Py_INCREF(Py_None);
    self->onMouseEnter = Py_None;
    Py_INCREF(Py_None);
    self->onMouseLeave = Py_None;

    return 0;
}

static PyObject*
element_register_tap_handler(Element_t *self, PyObject *args)
{
    PyObject *onTap;

    if(!PyArg_ParseTuple(args,"O",&onTap)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    self->onTap = onTap;

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
element_register_mouse_enter_handler(Element_t *self, PyObject *args)
{
    PyObject *onMouseEnter;

    if(!PyArg_ParseTuple(args,"O",&onMouseEnter)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    self->onMouseEnter = onMouseEnter;
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
element_register_mouse_leave_handler(Element_t *self, PyObject *args)
{
    PyObject *onMouseLeave;

    if(!PyArg_ParseTuple(args,"O",&onMouseLeave)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    self->onMouseLeave = onMouseLeave;
    Py_INCREF(Py_None);
    return Py_None;
}


static PyMethodDef element_methods[] = {
    { "register_tap_handler", 
        (PyCFunction)element_register_tap_handler, 
        METH_VARARGS, "Register Tap handler" },
    { "register_mouse_enter_handler", 
        (PyCFunction)element_register_mouse_enter_handler, 
        METH_VARARGS, "Register Mouse Enter handler" },
    { "register_mouse_leave_handler", 
        (PyCFunction)element_register_mouse_leave_handler, 
        METH_VARARGS, "Register Mouse Leave handler" },
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
    { "opacity", T_INT, offsetof(Element_t,opacity),0,"Opacity of element"},

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
    // Unused - GenericNew() is enough so far
}

PyTypeObject Element_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "inkface.element",                  /* tp_name */
    sizeof(Element_t),                  /* tp_basicsize */
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
    Py_TPFLAGS_DEFAULT|Py_TPFLAGS_BASETYPE,  /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
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
    RsvgHandle *handle = NULL;
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
        inkface_get_element(handle,element);

        // Create python object for Element
        PyTypeObject *pytype = NULL;
        PyObject *pyo;
        pytype = &Element_Type;
        ASSERT(pyo = pytype->tp_alloc(pytype,0));

        ((Element_t *)pyo)->x = element->x;
        ((Element_t *)pyo)->y = element->y;
        ((Element_t *)pyo)->w = element->w;
        ((Element_t *)pyo)->h = element->h;
        ((Element_t *)pyo)->order = element->order;
        ((Element_t *)pyo)->name = PyString_FromString(element->name);
        ((Element_t *)pyo)->id = PyString_FromString(element->id);
        //TODO: ((Element_t *)pyo)->surface->surface = element->surface;

        // Add python object to list
        PyList_Append(pyElementList,pyo);

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

    Element_Type.tp_new = PyType_GenericNew;
    Canvas_Type.tp_new = PyType_GenericNew;

    if (PyType_Ready(&Element_Type) < 0) return;
    if (PyType_Ready(&Canvas_Type) < 0) return;

    m = Py_InitModule("inkface",inkface_methods);

    PyModule_AddObject(m,"canvas",(PyObject *)&Canvas_Type);

}


/* INTERNAL FUNCTIONS */

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

void
paint(void *arg)
{
    Canvas_t *canvas = (Canvas_t *) arg;

    if(!canvas->dirt_count) return;

    PyObject *iterator = PyObject_GetIter(canvas->element_list);
    PyObject *item;
    while(item = PyIter_Next(iterator)){
        Element_t *el = (Element_t *)item;

        if(PyCallable_Check(el->draw)){
            // Call element's custom draw handler
        } else {
            // Call canvas's default draw method
        }

        Py_DECREF(item);
    }
    Py_DECREF(iterator);


    #ifdef DOUBLE_BUFFER
    XdbeBeginIdiom(canvas->dpy);
    XdbeSwapBuffers(canvas->dpy,&canvas->swapinfo,1);
    XSync(canvas->dpy,0);
    XdbeEndIdiom(canvas->dpy);
    #else
    XFlush(canvas->dpy);
    #endif

    decr_dirt_count(1);
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
