#include <Python.h>

#include <stdio.h>

static PyObject *canvas_run(PyObject *self,PyObject *pArgs)
{
    printf("Canvas RUN\n");
    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef canvas_methods[] =
{
    { "run",canvas_run,METH_VARARGS,NULL},
    { NULL, NULL }
};

DL_EXPORT(void)
initcanvasX(void)
{
    Py_InitModule("canvasX", canvas_methods);
}
