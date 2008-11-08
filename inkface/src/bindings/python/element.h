#ifndef __ELEMENT_H__
#define __ELEMENT_H__


//
// "element" type object
//

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

    PyObject *p_surface;

    // private 
    Element *element;

    // Callback handlers
    PyObject *onDraw;
    PyObject *onTap;
    PyObject *onMouseEnter;
    PyObject *onMouseLeave;
    PyObject *onKeyPress;

} Element_t;


#endif /* __ELEMENT_H__ */
