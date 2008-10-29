#include "Python.h"
#include "structmember.h"

typedef struct {
    PyObject_HEAD
    int i;
} Foo_t;

static PyMethodDef foo_methods[] = {
    {NULL, NULL, 0, NULL},
};

static PyMemberDef foo_members[] = {
    { "i",T_INT,offsetof(Foo_t,i),0,"i of Foo" },
    { NULL }
};

static PyObject *
p_foo_new (PyTypeObject *type, PyObject *args, PyObject *kwds)
{
}

static void
p_foo_dealloc(Foo_t *self)
{
}

static int
p_foo_init(Foo_t *self, PyObject *args, PyObject *kwds)
{
}

PyTypeObject Foo_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "simpy.foo",                        /* tp_name */
    sizeof(Foo_t),                      /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)p_foo_dealloc,          /* tp_dealloc */
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
    foo_methods,                        /* tp_methods */
    foo_members,                        /* tp_members */
    0,                                  /* tp_getset */
    0, /* &Foo_Type, */                 /* tp_base */
    0,                                  /* tp_dict */
    0,                                  /* tp_descr_get */
    0,                                  /* tp_descr_set */
    0,                                  /* tp_dictoffset */
    (initproc)p_foo_init,               /* tp_init */
    0,                                  /* tp_alloc */
    (newfunc)p_foo_new,                 /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};

static PyObject*
create_foo(PyObject *self, PyObject *args)
{
#ifdef FACTORY
    PyTypeObject *type = &Foo_Type;
    Foo_t *foobj = (Foo_t *)type->tp_alloc(type,0);
    foobj->i = 23;
#else
    Foo_t *foobj = NULL;
    foobj = PyObject_New(Foo_t,&Foo_Type);
    foobj->i = 23;
#endif

    return (PyObject *)foobj;
}

static PyMethodDef simpy_methods[] =
{
    { "create_foo", (PyCFunction)create_foo, METH_NOARGS, NULL },
    { NULL, NULL, 0, NULL},
};

DL_EXPORT(void)
initsimpy(void)
{
    PyObject *m;
    m = Py_InitModule("simpy",simpy_methods);

    if (PyType_Ready(&Foo_Type) < 0) return;
}

