
#include "Python.h"
#include "structmember.h"

#include <cairo.h>
#include <cairo-xlib.h>
#include <X11/Xatom.h>

#include "inkface.h"

#include "X11/keysym.h"

#ifdef DOUBLE_BUFFER
#include <X11/extensions/Xdbe.h>
#endif

#include "common.h"

#include "canvas-common.h"
#include "canvas-x.h"
#include "canvas.h"
#include "element.h"


void calculate_total_refcnt(Canvas_t *self,int line)
{
    PyObject *iterator;
    PyObject *item;
    int trc=0;
    int i=0;
    iterator = PyObject_GetIter(self->element_list);
    while(item = PyIter_Next(iterator)){
        trc += item->ob_refcnt;
        Py_DECREF(item);
        i++;
    }
    Py_DECREF(iterator);
    LOG("<%d> rc(%d) = %d",line,i,trc);
}


//
// "canvas" object methods and members
//

static void
p_canvas_dealloc(Canvas_t *self)
{
    ASSERT(self);
    if(self->cobject) {
        Py_BEGIN_ALLOW_THREADS

        self->cobject->cleanup(self->cobject);

        Py_END_ALLOW_THREADS

        free(self->cobject); 
        self->cobject = NULL;
    }
    self->ob_type->tp_free((PyObject *)self);
}

static PyObject*
p_canvas_reset_order(Canvas_t *self,PyObject *args)
{
    ASSERT(self);
    PyList_Sort(self->element_list);
    recalculate_clouds(self);
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
p_canvas_bring_to_front(Canvas_t *self,PyObject *args)
{
    Element_t *element;
    ASSERT(self);
    ASSERT(args);

    if(!PyArg_ParseTuple(args,"O",&element)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!element){
        Py_INCREF(Py_None);
        return Py_None;
    }

    int i = PySequence_Index(self->element_list,(PyObject *)element);

    ASSERT(i>=0);

    ASSERT(PySequence_DelItem(self->element_list,i) >= 0);
     

    PyList_Append(self->element_list,(PyObject *)element);

    // Print the list
    /*
    PyObject *iter = PyObject_GetIter(self->element_list);
    PyObject *item = NULL;
    int j = 0;
    while(item = PyIter_Next(iter)){
        LOG("%d. %s",j++,PyString_AS_STRING(PyObject_GetAttrString(item,"name")));
        Py_DECREF(item);
    }
    Py_DECREF(iter);
    */

    recalculate_clouds(self);

    self->cobject->inc_dirt_count(self->cobject,1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
p_canvas_draw(Canvas_t *self, PyObject *args)
{
    Element_t *element;
    ASSERT(self);
    ASSERT(args);

    if(!PyArg_ParseTuple(args,"O",&element)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!element){
        Py_INCREF(Py_None);
        return Py_None;
    }

    self->cobject->draw_elem(self->cobject,element->element);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
p_canvas_refresh(Canvas_t *self, PyObject *args)
{
    ASSERT(self && self->cobject)

    self->cobject->inc_dirt_count(self->cobject,1);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
p_canvas_register_elements_list(PyObject *self, PyObject *args)
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
p_canvas_register_elements(PyObject *self, PyObject *args)
{
    PyObject *elemDict_pyo;

    if(!PyArg_ParseTuple(args,"O",&elemDict_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!elemDict_pyo){
        Py_INCREF(Py_None);
        return Py_None;
    }

    ASSERT(PyDict_Check(elemDict_pyo));

    // Store a reference to this dict for passing to event handlers
    // TODO: This assumes only one usage of register_elements during the app
    //      When we support unregister_elements, hence implying multiple
    //      calls to register_elements, this will have to be fixed. 
    //      With this implementation, every call to register_elements will
    //      overwrite the dictionary object.
    Py_INCREF(elemDict_pyo);
    ((Canvas_t *)self)->element_dict = elemDict_pyo;

    PyObject *elemList_pyo = PyDict_Values(elemDict_pyo);
    PyObject *iterator = PyObject_GetIter(elemList_pyo);
    PyObject *item;

    ASSERT(iterator);

    while(item = PyIter_Next(iterator)){
        PyList_Append(((Canvas_t *)self)->element_list,item);
    }

    // The original element list generated by libaltsvg is sorted,
    // however after we load it as a dict in inkface. 
    // The extracted list from the dict doesn't necessarily have same order.
    // So we need to sort it again.
    // Element_t's richcompare method takes care of using "order" to sort
    PyList_Sort(((Canvas_t *)self)->element_list);

    Py_DECREF(iterator);

    Py_INCREF(Py_None);
    return Py_None;
}


static PyObject*
p_canvas_unregister_elements_list(Canvas_t *self, PyObject *args)
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
p_canvas_unregister_elements(Canvas_t *self, PyObject *args)
{
    PyObject *elemDict_pyo;

    if(!PyArg_ParseTuple(args,"O",&elemDict_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!elemDict_pyo){
        Py_INCREF(Py_None);
        return Py_None;
    }

    ASSERT(PyDict_Check(elemDict_pyo));

    //TODO:
    
    #if 0
    PyObject *iterator = PyObject_GetIter(elemDict_pyo);
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

static PyObject *
p_canvas_add(Canvas_t *self, PyObject *args)
{    
    PyObject *elemList_pyo = NULL;

    calculate_total_refcnt(self,__LINE__);

    PyObject *face_pyo;

    if(!PyArg_ParseTuple(args,"O",&face_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!face_pyo){
        Py_RETURN_FALSE;
    }

    // Check if this Face object is already added to the canvas
    if(PySequence_Contains(self->face_list,face_pyo)) Py_RETURN_FALSE;

    // Add Face object to the face_list of this canvas
    ASSERT(PyList_Append(self->face_list,face_pyo) >= 0);

    self->__face_list_dirty__ = TRUE;

    canvas_refresh_elements(self);

    calculate_total_refcnt(self,__LINE__);

    Py_RETURN_TRUE;
}

static PyObject *
p_canvas_remove(Canvas_t *self, PyObject *args)
{
    PyObject *face_pyo;

    if(!PyArg_ParseTuple(args,"O",&face_pyo)){
        PyErr_Clear();
        PyErr_SetString(PyExc_ValueError,"Invalid Arguments");
        return NULL;
    }

    if(!face_pyo){
        Py_INCREF(Py_None);
        return Py_None;
    }

    // Remove Face object from the canvas's face_list
    int i = PySequence_Index(self->face_list,face_pyo);
    if(i >= 0){
        ASSERT(PySequence_DelItem(self->face_list,i) >= 0);
    }

    PyList_Append(self->removed_face_list,face_pyo);

    self->__face_list_dirty__ = TRUE;

    Py_INCREF(Py_None);
    return Py_None;
}

static void
canvas_refresh_elements(Canvas_t *self)
{
    if(! self->__face_list_dirty__) return;

    PyObject *face_iter = PyObject_GetIter(self->face_list);    
    PyObject *face_item = NULL;

    PySequence_DelSlice(self->element_list,0,PyList_Size(self->element_list));
    while(face_item = PyIter_Next(face_iter))
    {
        PyObject *elem_dict = PyObject_GetAttrString(face_item,"elements");

        PyObject *elem_list = PyDict_Values(elem_dict);

        PyList_Sort(elem_list);

        PyObject *elem_iter = PyObject_GetIter(elem_list);
        PyObject *elem_item = NULL;
        while(elem_item = PyIter_Next(elem_iter))
        {
            PyList_Append(self->element_list,elem_item);
            Py_DECREF(elem_item);
        }
        Py_DECREF(elem_iter);

        Py_DECREF(elem_dict);
        Py_DECREF(elem_list);
        Py_DECREF(face_item);
    }
    Py_DECREF(face_iter);

    self->__face_list_dirty__ = FALSE;

    recalculate_clouds(self);
    
    PyObject *remface_iter = PyObject_GetIter(self->removed_face_list);
    PyObject *remface_item = NULL;
    while(remface_item = PyIter_Next(remface_iter))
    {
        PyObject_CallMethod(remface_item,"unload",NULL);        
        Py_DECREF(remface_item);
    }
    Py_DECREF(remface_iter);

    PySequence_DelSlice(self->removed_face_list,
            0,PyList_Size(self->removed_face_list));

    return;
}

#define INK_MAX(a,b) ((a>b)?a:b)
#define INK_MIN(a,b) ((a<b)?a:b)

/*
 * @method: recalculate_clouds
 *
 * @summary: This method compares surface extents of all existing widgets
            with the new widget and determines if the new widget will
            overlap with them. If it does overlap the existing widgets will 
            loose their isKeyActive and isPoinerActive statuses.
 * @param newWidget: New widget being appended to the widgetQ
            
            
    (ox0,oy0)<-------- ow -------->
           ^ ----------------------
           | |                    |
           | |                    |
          oh |                    |
           | |                    |
           v ---------------------- (ox1,oy1)
           
           
                        (nx0,ny0)<-------- nw -------->
                               ^ ----------------------
                               | |                    |
                               | |                    |
                              nh |     newWidget      |
                               | |                    |
                               | |                    |
                               v ---------------------- (nx1,ny1)
 
 */
void 
recalculate_clouds(Canvas_t *self)
{
    ASSERT(self);

    //LOG("recalculating clouds");
    //LOG("element list: ");
    int lsize = PyList_Size(self->element_list);

    int ox0,oy0,ox1,oy1,nx0,ny0,nx1,ny1;
    int i=0,j=0;

    PyObject *iter = PyObject_GetIter(self->element_list);
    PyObject *item = NULL;
    while(item = PyIter_Next(iter)){
        Py_DECREF(((Element_t *)item)->clouds);
        ((Element_t *)item)->clouds = PyList_New(0);
        Py_DECREF(item);
    }
    Py_DECREF(iter);

    for(; i<lsize; i++)
    {

        Element_t *ne = (Element_t *)PyList_GetItem(self->element_list,i);

        nx0 = ne->x;
        ny0 = ne->y;
        nx1 = nx0 + ne->w;
        ny1 = ny0 + ne->h;

        //LOG(" - %s (%d,%d) (%d,%d)",PyString_AsString(ne->name),
        //            nx0,ny0,nx1,ny1);

        for(j=0; j<i; j++)
        {
            Element_t *oe = (Element_t *)PyList_GetItem(self->element_list,j);

            ox0 = oe->x;
            oy0 = oe->y;
            ox1 = ox0 + oe->w;
            oy1 = oy0 + oe->h;

            //LOG("   - %s (%d,%d),(%d,%d)",PyString_AsString(oe->name),
            //            ox0,oy0,ox1,oy1);

            if ((ox0 < nx0 && ox1 < nx0) || (ox0 > nx1 && ox1 > nx1) || \
                (oy0 < ny0 && oy1 < ny0) || (oy0 > ny1 &&  oy1 > ny1))
            {
                continue;

            } else {
                PyObject *cloud = PyTuple_Pack(4,
                        PyInt_FromLong(INK_MAX(ox0,nx0)-ox0),
                        PyInt_FromLong(INK_MAX(oy0,ny0)-oy0),
                        PyInt_FromLong(INK_MIN(ox1,nx1)-ox0),
                        PyInt_FromLong(INK_MIN(oy1,ny1)-oy0));
                ASSERT(oe->clouds);
                PyList_Append((PyObject *)oe->clouds,cloud);
                //LOG(" %s - clouding %s at (%d,%d),(%d,%d)",
                //        PyString_AsString(ne->name),
                //        PyString_AsString(oe->name),
                //        (INK_MAX(ox0,nx0)-ox0),
                //        (INK_MAX(oy0,ny0)-oy0),
                //        (INK_MIN(ox1,nx1)-ox0),
                //        (INK_MIN(oy1,ny1)-oy0));
            }
        }
    }
}


static PyObject*
p_canvas_eventloop(Canvas_t *self, PyObject *args)
{
    self->cobject->show(self->cobject);
    
    int error_flag = 0;
    PyObject *result = NULL;

    /*
     * Setup the event listening
     */
    XSelectInput(((x_canvas_t *)self->cobject)->dpy, 
                    ((x_canvas_t *)self->cobject)->win, 
                    StructureNotifyMask|
                    PointerMotionMask|
                    ExposureMask|
                    KeyPressMask|
                    KeyReleaseMask);
    while(1)
    {
        XMotionEvent *mevent;
        XEvent event;
#ifdef HAS_XSP
        int pressure = 0;
#endif 
        PyObject *iterator;
        PyObject *item;

        Py_BEGIN_ALLOW_THREADS

        XNextEvent(((x_canvas_t *)self->cobject)->dpy,&event);

        Py_END_ALLOW_THREADS
        
        switch(event.type){
        case MapNotify:
            break;
        case KeyPress:
            {
                KeySym keysym;
                char buf[3] = "\0\0\0";
                XLookupString(&event.xkey,buf,1,&keysym,NULL);
                switch(keysym){
                case XK_BackSpace:
                case XK_Tab:
                case XK_Escape:
                    // For special keys clear the ASCII interpretation 
                    // of the key
                    memset(buf,0,3*sizeof(char));
                default:
                    break;
                }
                iterator = PyObject_GetIter(self->element_list);
                while(item = PyIter_Next(iterator)){
                    Element_t *el = (Element_t *)item;
                    if(PyCallable_Check(el->onKeyPress)){
                        result = PyObject_CallFunction(
                            el->onKeyPress,
                            "OOi",
                            el,
                            PyString_FromString(buf),
                            keysym);
                        if(!result) error_flag = 1;
                    }
                    Py_DECREF(item);
                }
                Py_DECREF(iterator);
            }
            break;
        case MotionNotify:
            mevent = (XMotionEvent *)(&event);
            iterator = PyObject_GetIter(self->element_list);
            int lsize = PyList_Size(self->element_list);
            //LOG("Current list size = %d",lsize);
            while(item = PyIter_Next(iterator)){

                Element_t *el = (Element_t *)item;

                // If element is under cloud at this point, then skip it
                if(element_under_cloud(el,mevent->x,mevent->y)) {
                    Py_DECREF(item);
                    continue;
                }

                int state = process_motion_event(el->element,mevent);
    
                if(state & POINTER_STATE_TAP)
                {
                    if(PyCallable_Check(el->onTap)) {
                        result = PyObject_CallFunction(el->onTap,
                            "O",el);
                        if(!result) error_flag = 1;
                    }
                }
    
                if(state & POINTER_STATE_LEAVE){
                    if(PyCallable_Check(el->onMouseLeave)) {
                        result = PyObject_CallFunction(el->onMouseLeave,
                            "O",el);
                        if(!result) error_flag = 1;
                    }
                }
    
                if(state & POINTER_STATE_ENTER){
                    if(PyCallable_Check(el->onMouseEnter)) {
                        result = PyObject_CallFunction(el->onMouseEnter,
                            "O",el);
                        if(!result) error_flag = 1;
                    }
                }

                Py_DECREF(item);
            }

            Py_DECREF(iterator);

            break;
        case DestroyNotify:
            Py_INCREF(Py_None);
            return Py_None;
        default:
            #ifdef HAS_XSP
            iterator = PyObject_GetIter(self->element_list);
            while(item = PyIter_Next(iterator)){

                Element_t *el = (Element_t *)item;
                
                pressure = calculate_pressure(el->element,&event);
                if(pressure > 20){
                    if(PyCallable_Check(el->onTap)) {
                        result = PyObject_CallFunction(el->onTap,
                            "OO",el,self->element_dict);
                        if(!result) error_flag = 1;
                    }
                }
                Py_DECREF(item);
            }
            Py_DECREF(iterator);
            #endif
            break;
        } // end of switch 

        // The even callback might have removed some faces from the canvas
        // Check the to_remove_face_list and cleanup its elements from
        // the canvas's list
        canvas_refresh_elements(self);

        if(error_flag){
            return NULL;
        }

        // Check if shutting_down was set during above event processing
        if(self->cobject->shutting_down){
            //Py_XDECREF(x_canvas);
            Py_INCREF(Py_None);
            return Py_None;
        }
    } // end of infinite while loop

    Py_INCREF(Py_None);
    return Py_None;

}

static PyMethodDef canvas_methods[] = {
    { "register_elements", (PyCFunction)p_canvas_register_elements, 
        METH_VARARGS, "[deprecated] Register elements with canvas" },
    { "unregister_elements", (PyCFunction)p_canvas_unregister_elements, 
        METH_VARARGS, "[deprecated] Unregister elements from canvas" },
    { "eventloop", (PyCFunction)p_canvas_eventloop, 
        METH_NOARGS, "Make canvas process events in infinite loop" },
    { "draw", (PyCFunction)p_canvas_draw, 
        METH_VARARGS, "Draw the element canvas" },
    { "bring_to_front", (PyCFunction)p_canvas_bring_to_front,
        METH_VARARGS, "Bring element to the front" },
    { "reset_order", (PyCFunction)p_canvas_reset_order,
        METH_VARARGS, "Reset the order of canvas's elements" },
    { "refresh", (PyCFunction)p_canvas_refresh, 
        METH_NOARGS, "Refresh the canvas" },
    { "add", (PyCFunction)p_canvas_add, 
        METH_VARARGS, "Add a Face object to the canvas" },
    { "remove", (PyCFunction)p_canvas_remove, 
        METH_VARARGS, "Remove the Face object from the canvas" },
    {NULL, NULL, 0, NULL},
};

static PyMemberDef canvas_members[] = {
    { "width", T_INT, offsetof(Canvas_t,width),0,"Width of Canvas"},
    { "height", T_INT, offsetof(Canvas_t,height),0,"Height of Canvas"},
    { "timeout", T_INT, offsetof(Canvas_t,timeout),0,"Timeout in msec"},
    { "fullscreen", T_OBJECT, offsetof(Canvas_t,fullscreen),0,
        "Fullscreen flag"},
    { "elements", T_OBJECT, offsetof(Canvas_t,element_list),0,
            "Elements currently registered with Canvas"},
    { "onTimer", T_OBJECT, offsetof(Canvas_t,onTimer),0,
            "Timeout handler"},
    { NULL }
};


PyTypeObject Canvas_Type = {
    PyObject_HEAD_INIT(NULL)
    0,                                  /* ob_size */
    "inkface.canvas",                   /* tp_name */
    sizeof(Canvas_t),                   /* tp_basicsize */
    0,                                  /* tp_itemsize */
    (destructor)p_canvas_dealloc,       /* tp_dealloc */
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
    0,                                  /* tp_init */
    0,                                  /* tp_alloc */
    0,                                  /* tp_new */
    0,                                  /* tp_free */
    0,                                  /* tp_is_gc */
    0,                                  /* tp_bases */
};



