
#include "Python.h"
#include "structmember.h"

#include <cairo.h>
#include <cairo-xlib.h>

#include "pycairo.h"

#include "inkface.h"

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "common.h"

#include "element.h"

//
// "element" object methods and members
//

extern Pycairo_CAPI_t *Pycairo_CAPI;

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
    Py_INCREF(Py_None);
    self->onKeyPress = Py_None;

    self->clouds = PyList_New(0);

    return 0;
}

static PyObject*
element_refresh(Element_t *self,PyObject *args)
{
    g_string_free(self->element->text,TRUE);
    self->element->text = g_string_new(
        PyString_AsString(self->text));
    inkface_get_element(self->element,TRUE);

    // Release ownership of old pycairo surface object
    Py_DECREF(self->p_surface);
    ASSERT(self->element->surface);
    ASSERT(self->p_surface = PycairoSurface_FromSurface(
                        self->element->surface,NULL));

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
    { "onKeyPress", T_OBJECT,offsetof(Element_t,onKeyPress),0,
                    "Keyboard key handler"},
    { NULL }
};

static PyObject *
element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    Element_t *self;

    self = (Element_t *)type->tp_alloc(type,0);

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
    if (self->onKeyPress) Py_DECREF(self->onKeyPress);

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
    if(self->p_surface){
        //TODO: free(self->p_surface);
    }

    self->ob_type->tp_free((PyObject *)self);
}

int
element_under_cloud(Element_t *self,int x, int y)
{
    int cx0,cy0,cx1,cy1,rx,ry;
    PyObject *iter = PyObject_GetIter(self->clouds);

    PyObject *item;
    // Conver incoming coordinates with reference to element coordinates.
    rx = x - self->x;
    ry = y - self->y;

    while(item = PyIter_Next(iter))
    {
        ASSERT(PyTuple_Size(item) == 4);
        cx0 = PyInt_AsLong(PyTuple_GetItem(item,0));
        cy0 = PyInt_AsLong(PyTuple_GetItem(item,1));
        cx1 = PyInt_AsLong(PyTuple_GetItem(item,2));
        cy1 = PyInt_AsLong(PyTuple_GetItem(item,3));
    
        //LOG("%s (%d-%d,%d-%d) - (%d,%d),(%d,%d)",
        //        PyString_AsString(self->name),
        //        x,self->x,y,self->y,cx0,cy0,cx1,cy1);

        // If following expression is true, then this element is under cloud
        if((rx > cx0) && (rx < cx1) && (ry > cy0) && (ry < cy1))
        {
            Py_DECREF(iter);
            //LOG("%s clouded at (%d,%d)",PyString_AsString(self->name),x,y);
            return TRUE;
        }
    }

    //LOG("%s not clouded at (%d,%d)",PyString_AsString(self->name),x,y);
    Py_DECREF(iter);
    return FALSE;
}

PyTypeObject Element_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "inkface.element",                  /* tp_name */
    sizeof(Element_t),                  /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor) element_dealloc,       /* tp_dealloc */
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
    (richcmpfunc) element_richcompare,  /* tp_richcompare */
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



