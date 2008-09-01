#include "inkface.h"
#include "string.h"

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
    if (!(el->on_mouse_over)) return;

    result = g_list_find_custom(
        elemList,el->on_mouse_over,compare_element_by_name); 

    if(!result) return;

    ASSERT(elmo = (Element *)result->data);

    elmo->type = glow ? !ELEM_TYPE_TRANSIENT:ELEM_TYPE_TRANSIENT;

    signal_paint();
}

void onKeyEnter(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,TRUE);
}

void onKeyLeave(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,FALSE);
}

void filter_key_buttons(gpointer data, gpointer userdata)
{
    GList **button_list = (GList **)userdata;

    char *element_name = ((Element *)data)->name;

    if(element_name && 
        !strncmp(element_name,"key",3) &&
        strlen(element_name) == 4)
    {
        /* button_list items should not be freed by the app.
         * the button_list itself can be freed
         */
        *button_list = g_list_prepend(*button_list,(Element *)data); 
    }
}

void wire_logic(GList *element_list)
{
    GList *key_button_list = NULL;

    g_list_foreach(element_list, filter_key_buttons, &key_button_list);

    GList *iter = key_button_list;

    while(iter)
    {
        Element *key_element = (Element *)(iter->data);
        key_element->onMouseEnter = onKeyEnter;
        key_element->onMouseLeave = onKeyLeave;
        iter = iter->next;
    }

}

int main(int argc, char *argv[])
{

    if(argc < 2){
        printf("%s <svg-filepath>\n",argv[0]);
        exit(0);
    }

    init_backend(argv[1]);

    GList *element_list = load_element_list();

    wire_logic(element_list);

    fork_painter_thread();

    eventloop();

    cleanup_backend();

    return 0;
}
