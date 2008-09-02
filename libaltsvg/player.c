#include "rsvg.h"
#include "inkface.h"

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

void
toggle_glow(Element *el, GList *elemList,gboolean glow)
{
    GList *result;
    Element *elmo;
    ASSERT(el->on_mouse_over);
    ASSERT(result = g_list_find_custom(
        elemList,el->on_mouse_over,compare_element_by_name)); 
    ASSERT(elmo = (Element *)result->data);

    elmo->type = glow ? !ELEM_TYPE_TRANSIENT:ELEM_TYPE_TRANSIENT;

    signal_paint();
}

/*
 * Event Handlers
 */

void
onNextButtonMouseEnter(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,TRUE);
}

void
onNextButtonMouseLeave(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,FALSE);
}

void
onPrevButtonMouseEnter(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,TRUE);
}

void
onPrevButtonMouseLeave(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,FALSE);
}

/*
 * Wire the event handlers with the elements
 */

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

int main(int argc, char *argv[])
{

    if(argc < 2){
        printf("%s <svg-filepath>\n",argv[0]);
        exit(0);
    }

    init_backend(argv[1],FALSE);

    GList *element_list = load_element_list();

    wire_logic(element_list);

    fork_painter_thread();

    eventloop();

    cleanup_backend();

    return 0;
}
