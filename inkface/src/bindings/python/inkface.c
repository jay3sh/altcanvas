
#include "Python.h"
#include "structmember.h"

#include <cairo.h>
#include <cairo-xlib.h>

#include "pycairo.h"

#include "inkface.h"

#include "X11/keysym.h"

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif


#include "common.h"

#include "canvas-common.h"
#include "canvas-x.h"
#include "canvas-gl.h"

#include "canvas.h"
#include "element.h"


Pycairo_CAPI_t *Pycairo_CAPI;
//TODO: Make canvas singleton
Canvas_t *x_canvas = NULL;
Canvas_t *gl_canvas = NULL;


void paint(void *arg);

extern PyTypeObject Canvas_Type;
extern PyTypeObject Element_Type;

/*
 * "inkface" module
 */
static PyObject*
inkface_loadsvg_list(PyObject *self, PyObject *args)
{
    char *svgname;
    Element *element;
    PyObject *p_elist = PyList_New(0);

    ASSERT(PyArg_ParseTuple(args,"s",&svgname))
        
    ASSERT(svgname)

    GList *elist = load_element_list(svgname);

    // Create Python list of elements

    GList *elem_list_head = elist;

    while(elist)
    {
        ASSERT(element = (Element *)elist->data);

        // 
        // Create python object for Element
        // 
        PyTypeObject *pytype = NULL;
        Element_t *pyo;
        pytype = &Element_Type;
        ASSERT(pyo = (Element_t *)pytype->tp_alloc(pytype,0));

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
        pyo->p_surface = PycairoSurface_FromSurface(element->surface,NULL);

        pyo->element = element;

        // Add python object to list
        PyList_Append(p_elist,(PyObject *)pyo);

        // jump to next
        elist = elist->next;
    }

    return p_elist;

}

static PyObject*
inkface_loadsvg(PyObject *self, PyObject *args)
{
    char *svgname;
    Element *element;
    PyObject *p_edict = PyDict_New();
    ASSERT(p_edict);

    ASSERT(PyArg_ParseTuple(args,"s",&svgname))
        
    ASSERT(svgname)

    GList *elist = load_element_list(svgname);

    // Create Python dictionary of elements

    GList *elem_list_head = elist;

    while(elist)
    {
        ASSERT(element = (Element *)elist->data);

        // 
        // Create python object for Element
        // 
        PyTypeObject *pytype = NULL;
        Element_t *pyo;
        pytype = &Element_Type;
        ASSERT(pyo = (Element_t *)pytype->tp_alloc(pytype,0));

        // TODO: use standard element_init
        pyo->x = element->x;
        pyo->y = element->y;
        pyo->w = element->w;
        pyo->h = element->h;
        pyo->order = element->order;
        pyo->name = PyString_FromString(element->name);
        pyo->id = PyString_FromString(element->id);
        pyo->clouds = (PyListObject *)PyList_New(0);
        if(element->text){
            pyo->text = PyString_FromString(element->text->str);
        }
        pyo->p_surface = PycairoSurface_FromSurface(element->surface,NULL);

        pyo->element = element;

        // Add python object to dictionary
        PyDict_SetItem(p_edict,PyString_FromString(element->name),
                        (PyObject *)pyo);

        // jump to next
        elist = elist->next;
    }

    return p_edict;

}

static PyObject*
inkface_create_X_canvas(PyObject *self, PyObject *args, PyObject *kwds)
{
    //if(x_canvas){
    //    return (PyObject *)x_canvas;
    //}
    
    ASSERT(x_canvas = PyObject_New(Canvas_t,&Canvas_Type));

    /*
    PyTypeObject *type = &Canvas_Type;
    ASSERT(x_canvas = (Canvas_t *)type->tp_alloc(type,0));
    */

    ASSERT(x_canvas->cobject = (canvas_t *)x_canvas_new());

    // Parse keyword args
    #define DEFAULT_WIDTH 800
    #define DEFAULT_HEIGHT 480 
    x_canvas->width=0; 
    x_canvas->height=0;
    x_canvas->fullscreen = Py_False;
    x_canvas->timeout = 0;
    x_canvas->onTimer = NULL;
    static char *kwlist[] = {"width", "height", "fullscreen", NULL};

    ASSERT(PyArg_ParseTupleAndKeywords(args, kwds, "|iiO", kwlist, 
                  &(x_canvas->width), &(x_canvas->height), &(x_canvas->fullscreen)))

    if(x_canvas->width <= 0) x_canvas->width = DEFAULT_WIDTH;
    if(x_canvas->height <= 0) x_canvas->height = DEFAULT_HEIGHT;

    //
    // Fullscreen preferences:
    //
    // 1. env var INKFACE_FULLSCREEN 
    // 2. kwd arg fullscreen 
    //
    char *env_fullscreen = getenv("INKFACE_FULLSCREEN");
    if(env_fullscreen && !strncmp(env_fullscreen,"TRUE",4)){
        x_canvas->fullscreen = Py_True;
    } else {
        if((x_canvas->fullscreen == NULL) || (!PyBool_Check(x_canvas->fullscreen))) {
            x_canvas->fullscreen = Py_False;
        } else {
            if(x_canvas->fullscreen == Py_True){
                x_canvas->fullscreen = Py_True;
            } else {
                x_canvas->fullscreen = Py_False;
            }
        }
    }


    // Initialize multi thread support for Python interpreter
    PyEval_InitThreads();

    x_canvas->cobject->init(x_canvas->cobject,
                        x_canvas->width, 
                        x_canvas->height, 
                        (x_canvas->fullscreen == Py_True));

    ((x_canvas_t *)x_canvas->cobject)->register_paint_function(
                        ((x_canvas_t *)x_canvas->cobject),
                        paint,
                        x_canvas);

    // Initialize the active element list
    x_canvas->element_list = PyList_New(0);

    return (PyObject *)x_canvas;
}


void gl_display(void)
{

}

static PyObject*
inkface_create_GL_canvas(PyObject *self, PyObject *args, PyObject *kwds)
{
#ifdef HAS_OPENGL
    //if(gl_canvas){
    //    return (PyObject *)gl_canvas;
    //}
    
    ASSERT(gl_canvas = PyObject_New(Canvas_t,&Canvas_Type));

    /*
    PyTypeObject *type = &Canvas_Type;
    ASSERT(gl_canvas = (Canvas_t *)type->tp_alloc(type,0));
    */

    ASSERT(gl_canvas->cobject = (canvas_t *)gl_canvas_new());

    // Parse keyword args
    #define DEFAULT_WIDTH 800
    #define DEFAULT_HEIGHT 480 
    gl_canvas->width=0; 
    gl_canvas->height=0;
    gl_canvas->fullscreen = Py_False;
    gl_canvas->timeout = 0;
    gl_canvas->onTimer = NULL;
    static char *kwlist[] = {"width", "height", "fullscreen", NULL};

    ASSERT(PyArg_ParseTupleAndKeywords(args, kwds, "|iiO", kwlist, 
                  &(gl_canvas->width), &(gl_canvas->height), &(gl_canvas->fullscreen)))

    if(gl_canvas->width <= 0) gl_canvas->width = DEFAULT_WIDTH;
    if(gl_canvas->height <= 0) gl_canvas->height = DEFAULT_HEIGHT;

    //
    // Fullscreen preferences:
    //
    // 1. env var INKFACE_FULLSCREEN 
    // 2. kwd arg fullscreen 
    //
    char *env_fullscreen = getenv("INKFACE_FULLSCREEN");
    if(env_fullscreen && !strncmp(env_fullscreen,"TRUE",4)){
        gl_canvas->fullscreen = Py_True;
    } else {
        if((gl_canvas->fullscreen == NULL) || (!PyBool_Check(gl_canvas->fullscreen))) {
            gl_canvas->fullscreen = Py_False;
        } else {
            if(gl_canvas->fullscreen == Py_True){
                gl_canvas->fullscreen = Py_True;
            } else {
                gl_canvas->fullscreen = Py_False;
            }
        }
    }


    // Initialize multi thread support for Python interpreter
    PyEval_InitThreads();

    gl_canvas->cobject->init(gl_canvas->cobject,
                        gl_canvas->width, 
                        gl_canvas->height, 
                        (gl_canvas->fullscreen == Py_True));

    ((gl_canvas_t *)gl_canvas->cobject)->register_display_function(
                        ((gl_canvas_t *)gl_canvas->cobject),
                        gl_display);

    // Initialize the active element list
    gl_canvas->element_list = PyList_New(0);

    return (PyObject *)gl_canvas;
#else // HAS_OPENGL
    PyErr_Clear();
    PyErr_SetString(PyExc_Exception,"OpenGL support is not compiled in");
    return NULL;
#endif // HAS_OPENGL
}

static PyObject*
inkface_exit(PyObject *self, PyObject *args)
{
    if(x_canvas && x_canvas->cobject){
        x_canvas->cobject->shutting_down = TRUE;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef inkface_methods[] =
{
    { "loadsvg", 
        (PyCFunction)inkface_loadsvg, METH_VARARGS, NULL },
    { "create_X_canvas", 
        (PyCFunction)inkface_create_X_canvas, METH_KEYWORDS, NULL },
    { "create_GL_canvas", 
        (PyCFunction)inkface_create_GL_canvas, METH_KEYWORDS, NULL },
    { "exit", 
        (PyCFunction)inkface_exit, METH_NOARGS, NULL },
    { NULL, NULL, 0, NULL},
};

DL_EXPORT(void)
initinkface(void)
{
    PyObject *m;

    Pycairo_IMPORT;

    rsvg_init();

    if (PyType_Ready(&Element_Type) < 0) return;
    if (PyType_Ready(&Canvas_Type) < 0) return;

    m = Py_InitModule("inkface",inkface_methods);

    PyModule_AddIntConstant(m,"KeyBackspace",XK_BackSpace);
    PyModule_AddIntConstant(m,"KeyTab",XK_Tab);
    PyModule_AddIntConstant(m,"KeyEscape",XK_Escape);
    PyModule_AddIntConstant(m,"KeyEnter",XK_Return);
    PyModule_AddIntConstant(m,"KeySpace",XK_space);
}

/* INTERNAL FUNCTIONS */
void paint(void *arg)
{
    Canvas_t *canvas = (Canvas_t *) arg;
    PyObject *result = NULL;
    int error_flag = 0;
    ASSERT(canvas);
    ASSERT(canvas->cobject);

    if(canvas->timeout){
        unsigned int timer_step = canvas->timeout/REFRESH_INTERVAL_MSEC;
        canvas->cobject->timer_counter++;
        canvas->cobject->timer_counter = \
            canvas->cobject->timer_counter % timer_step;
    }

    if((canvas->cobject->timer_counter == 0) || (canvas->cobject->dirt_count))
    {

        // BEGIN - Python thread safety code block
        PyGILState_STATE gstate;
        gstate = PyGILState_Ensure();
    
        if(canvas->cobject->timer_counter == 0){
            if(canvas->onTimer && PyCallable_Check(canvas->onTimer)){
                result = PyObject_CallFunction(canvas->onTimer,NULL);
                if(!result){
                    PyErr_Print();
                    error_flag = 1;
                }
            }
        }
        
        PyObject *iterator = PyObject_GetIter(canvas->element_list);
        PyObject *item;
        while(item = PyIter_Next(iterator)){
            Element_t *el = (Element_t *)item;
    
            if(PyCallable_Check(el->onDraw)){
                // Call element's custom draw handler
                result = PyObject_CallFunction(el->onDraw,"O",el);
                if(!result){
                    PyErr_Print();
                    error_flag = 1;
                }
            } else {
                // Call canvas's default draw method
                canvas->cobject->draw_elem(canvas->cobject,el->element);
            }

            Py_DECREF(item);
        }
        Py_DECREF(iterator);
    
        PyGILState_Release(gstate);
        // END - Python thread safety code block
    
        #ifdef DOUBLE_BUFFER
        XdbeBeginIdiom(((x_canvas_t *)canvas->cobject)->dpy);
        XdbeSwapBuffers(((x_canvas_t *)canvas->cobject)->dpy,
                            &((x_canvas_t *)canvas->cobject)->swapinfo,
                            1);
        XSync(((x_canvas_t *)canvas->cobject)->dpy,0);
        XdbeEndIdiom(((x_canvas_t *)canvas->cobject)->dpy);
        #else
        XFlush(((x_canvas_t *)canvas->cobject)->dpy);
        #endif

        canvas->cobject->dec_dirt_count(canvas->cobject,1);

        if(error_flag){
            canvas->cobject->shutting_down = 1;
        }
    }
}

