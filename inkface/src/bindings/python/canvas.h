#ifndef __CANVAS_H__
#define __CANVAS_H__

//
// "canvas" type object
//

typedef struct {
    PyObject_HEAD

    canvas_t *cobject;

    int width;
    int height;
    PyObject *fullscreen;

    PyObject *element_dict;
    PyObject *element_list;

    // Painting control members
    unsigned int timeout;

    PyObject *onTimer;

} Canvas_t;

static void 
    p_canvas_dealloc(Canvas_t *self);
static PyObject* 
    p_canvas_draw(Canvas_t *self, PyObject *args);
static PyObject*
    p_canvas_refresh(Canvas_t *self, PyObject *args);
static PyObject*
    p_canvas_set_timer(Canvas_t *canvas, PyObject *args);
static PyObject*
    p_canvas_register_elements(PyObject *self, PyObject *args);
static PyObject*
    p_canvas_unregister_elements(Canvas_t *self, PyObject *args);
static PyObject*
    p_canvas_eventloop(Canvas_t *self, PyObject *args);

// Internal helper functions

void recalculate_clouds(Canvas_t *self);

#endif /* __CANVAS_H__ */
