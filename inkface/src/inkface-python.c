
#include "Python.h"
#include "structmember.h"

#include "inkface.h"


RsvgHandle *rsvg_handle_from_file(const char *filename);

/*
 * "canvas" type object
 */

typedef struct {
    int dpy; 
} Canvas_t;

static PyMethodDef canvas_methods[] = {
    {NULL, NULL, 0, NULL},
};

static PyObject *
canvas_new (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
}

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
    Py_TPFLAGS_DEFAULT,                 /* tp_flags */
    0,                                  /* tp_doc */
    0,                                  /* tp_traverse */
    0,                                  /* tp_clear */
    0,                                  /* tp_richcompare */
    0,                                  /* tp_weaklistoffset */
    0,                                  /* tp_iter */
    0,                                  /* tp_iternext */
    canvas_methods,                     /* tp_methods */
    0,                                  /* tp_members */
    0,                                  /* tp_getset */
    0, /* &Canvas_Type, */              /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)canvas_new,                /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};

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

    PyObject *name;
    PyObject *id;

    int opacity;

    PycairoSurface_t *surface;    

} Element_t;

static PyMethodDef element_methods[] = {
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
    { NULL }
};

static PyObject *
element_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{

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
        ((Element_t *)pyo)->surface = element->surface;

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
    rsvg_init();

    if (PyType_Ready(&Element_Type) < 0) return;

    Py_InitModule("inkface",inkface_methods);
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

