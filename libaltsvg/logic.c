#include "rsvg.h"
#include "inkface.h"

/*
 * Event Handlers
 */

void
onNextButtonMouseEnter(Element *el)
{
    LOG("<<%s>>",__FUNCTION__);
}

void
onNextButtonMouseLeave(Element *el)
{
    LOG("<<%s>>",__FUNCTION__);
}

void
onPrevButtonMouseEnter(Element *el)
{
    LOG("<<%s>>",__FUNCTION__);
}

void
onPrevButtonMouseLeave(Element *el)
{
    LOG("<<%s>>",__FUNCTION__);
}

/*
 * Wire the event handlers with the elements
 */

gint 
compare_element_by_name(
    gconstpointer listitem,
    gconstpointer name)
{
    ASSERT(listitem);
    ASSERT(name);
    Element *element = (Element *)listitem;
    if(element->name){
        return strncmp(element->name,
                        (const char *)name,
                        strlen((const char *)name));
    } else {
        return -1;
    }
}

void wire_logic(GList *elemList)
{
    GList *result = NULL;
    Element *prevButton=NULL, *nextButton=NULL;

    ASSERT(result = 
        g_list_find_custom(elemList,"prevButton",compare_element_by_name)); 
    ASSERT(prevButton = (Element *)result->data);

    ASSERT(result = 
        g_list_find_custom(elemList,"nextButton",compare_element_by_name)); 
    ASSERT(nextButton = (Element *)result->data);

    prevButton->onMouseEnter = onPrevButtonMouseEnter;
    prevButton->onMouseLeave = onPrevButtonMouseLeave;
    nextButton->onMouseEnter = onNextButtonMouseEnter;
    nextButton->onMouseLeave = onNextButtonMouseLeave;
}

