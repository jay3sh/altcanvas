
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

#include "canvas.h"
#include "element.h"


Pycairo_CAPI_t *Pycairo_CAPI;
//TODO: Make canvas singleton
Canvas_t *x_canvas = NULL;


void paint(void *arg);

extern PyTypeObject Canvas_Type;
extern PyTypeObject Element_Type;

/*
 * "inkface" module
 */
static PyObject*
inkface_loadsvg(PyObject *self, PyObject *args)
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

    ASSERT(x_canvas->cobject = canvas_new());

    // Parse keyword args
    #define DEFAULT_WIDTH 800
    #define DEFAULT_HEIGHT 480 
    x_canvas->width=0; 
    x_canvas->height=0;
    x_canvas->fullscreen = Py_False;
    x_canvas->timer_step = 0;
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
                        (x_canvas->fullscreen == Py_True),
                        paint,
                        (void *)x_canvas);

    // Initialize the active element list
    x_canvas->element_list = PyList_New(0);

    return (PyObject *)x_canvas;
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

    if(canvas->timer_step){
        canvas->cobject->timer_counter++;
        canvas->cobject->timer_counter = \
            canvas->cobject->timer_counter % canvas->timer_step;
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
        XdbeBeginIdiom(canvas->cobject->dpy);
        XdbeSwapBuffers(canvas->cobject->dpy,&canvas->cobject->swapinfo,1);
        XSync(canvas->cobject->dpy,0);
        XdbeEndIdiom(canvas->cobject->dpy);
        #else
        XFlush(canvas->cobject->dpy);
        #endif

        canvas->cobject->dec_dirt_count(canvas->cobject,1);

        if(error_flag){
            canvas->cobject->shutting_down = 1;
        }
    }
}

