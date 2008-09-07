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
        int diff = strncmp(element->name,
                        (const char *)name,
                        strlen((const char *)name));
        /* Make sure it's an exact name match. 
         * Avoid false matches where one is a left aligned substring
         * of another
         */
        if(!diff){
            if(strlen(element->name) != strlen(name))
                return -1;
        }
        return diff;
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

    elmo->opacity = glow ? 100:0;

}

/*
 * Event handlers
 */

/*
 * Input event handlers
 */

void onKeyEnter(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,TRUE);
    incr_dirt_count(1);
}

void onKeyLeave(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,FALSE);
    incr_dirt_count(1);
}

void onExit(Element *el, void *userdata)
{
    cleanup_backend();
    exit(0);
}

/*
 * Drawing event handlers
 */
void
onKeyDraw(Element *element, void *userdata)
{
    if(element->opacity){
        cairo_t *ctx = (cairo_t *)userdata;
        cairo_set_source_surface(ctx,
            element->surface,element->x,element->y);
        cairo_paint(ctx);
    }
}

gboolean str_equal(const char *in, const char *ref)
{
   if(!strncmp(in,ref,strlen(ref)) && (strlen(in) == strlen(ref)))
        return TRUE;

   return FALSE;
}

void wire_element(gpointer data, gpointer userdata)
{
    Element *el = (Element *)data;

    if(!strncmp(el->name,"key",3)){
        if(strstr(el->name,"Glow")){
            /* Glowing button */
            el->opacity = 0;
        } else {
            /* Original button */
            el->opacity = 100;
        }
        el->onMouseEnter = onKeyEnter;
        el->onMouseLeave = onKeyLeave;
        el->draw = onKeyDraw;

        return;
    }

    if(str_equal(el->name,"exitDoor")){
        el->onMouseEnter = onExit;
    }
}

void wire_logic(GList *element_list)
{
    g_list_foreach(element_list,wire_element,NULL);
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
