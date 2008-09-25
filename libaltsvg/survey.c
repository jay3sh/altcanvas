
#include "inkface.h"
#include "string.h"

#define SVG_PATH "/photos/inkfun/survey/survey.svg"

int screen_num = 0;

void
onKeyDraw(Element *element, void *userdata)
{
    if((screen_num <= 0) || (screen_num >= 4))
        return;

    if(strstr(element->name,"Tapped")){
        // by default hide Tapped buttons
        return;
    } else {
        cairo_t *ctx = (cairo_t *)userdata;
        cairo_set_source_surface(ctx,
            element->surface,element->x,element->y);
        cairo_paint(ctx);
    }
}

void
onQuestionNumDraw(Element *element, void *userdata)
{
    if(strstr(element->name,"Tick")){
        // by default hide Tick labels 
        return;
    } else {
        cairo_t *ctx = (cairo_t *)userdata;
        cairo_set_source_surface(ctx,
            element->surface,element->x,element->y);
        cairo_paint(ctx);
    }
}

void
onQuestionDraw(Element *element, void *userdata)
{
    if((screen_num > 0) && (screen_num < 4)){
        char question_to_show[16];
        snprintf(question_to_show,16,"labelQ%d",screen_num);
        if(str_equal(element->name,question_to_show)){
            cairo_t *ctx = (cairo_t *)userdata;
            cairo_set_source_surface(ctx,
                element->surface,element->x,element->y);
            cairo_paint(ctx);
        }
    } else {
        return;
    }
}

void
onScaleLabelDraw(Element *element, void *userdata)
{
    if((screen_num <= 0) || (screen_num >= 4))
        return;

    cairo_t *ctx = (cairo_t *)userdata;
    cairo_set_source_surface(ctx,
        element->surface,element->x,element->y);
    cairo_paint(ctx);
}

void
onButtonStartDraw(Element *element,void *userdata)
{
    if(screen_num != 0) return;

    cairo_t *ctx = (cairo_t *)userdata;
    cairo_set_source_surface(ctx,
        element->surface,element->x,element->y);
    cairo_paint(ctx);
}

void 
onLabelFinishDraw(Element *element,void *userdata)
{
    if(screen_num != 4) return;

    cairo_t *ctx = (cairo_t *)userdata;
    cairo_set_source_surface(ctx,
        element->surface,element->x,element->y);
    cairo_paint(ctx);
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
    if(!strncmp(el->name,"labelQNum",strlen("labelQNum"))){
        el->draw = onQuestionNumDraw;
    } else if( !strncmp(el->name,"labelQ",strlen("labelQ")) &&
        (strlen(el->name) == strlen("labelQ")+1)){ // will break for >9 que
        el->draw = onQuestionDraw;
    } else if(!strncmp(el->name,"key",strlen("key"))){
        el->draw = onKeyDraw;
    } else if(str_equal(el->name,"labelPoor") ||
                str_equal(el->name,"labelExcellent"))
    {
        el->draw = onScaleLabelDraw;
    } else if(str_equal(el->name,"buttonStart") ||
                str_equal(el->name,"labelStart")){
        el->draw = onButtonStartDraw;
    } else if(str_equal(el->name,"labelFinish") ||
                str_equal(el->name,"labelSubmitted")){
        el->draw = onLabelFinishDraw;
    }

}

void wire_logic(GList *element_list)
{
    g_list_foreach(element_list,wire_element,NULL);
}

int main(int argc, char *argv[])
{
    init_backend(SVG_PATH,FALSE);

    GList *element_list = load_element_list();

    ASSERT(element_list);

    wire_logic(element_list);

    fork_painter_thread();

    eventloop();

    cleanup_backend();

    return 0;

}
