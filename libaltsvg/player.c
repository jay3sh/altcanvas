#include "rsvg.h"
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
    ASSERT(el->on_mouse_over);
    ASSERT(result = g_list_find_custom(
        elemList,el->on_mouse_over,compare_element_by_name)); 
    ASSERT(elmo = (Element *)result->data);

    elmo->opacity = 100;

    signal_paint();
}

/*
 * Event Handlers
 */

void
onNextButtonMouseEnter(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,TRUE);
    incr_dirt_count(6);
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
    incr_dirt_count(6);
}

void
onPrevButtonMouseLeave(Element *el, void *userdata)
{
    toggle_glow(el,(GList *)userdata,FALSE);
}

void
onGlowDraw(Element *el, void *userdata)
{
    if(el->opacity > 0){
        cairo_t *ctx = (cairo_t *)userdata;
        cairo_set_source_surface(ctx,el->surface,el->x,el->y);
        cairo_paint_with_alpha(ctx,el->opacity/100.);
        el->opacity -= 20;

        if(el->opacity < 0){
            el->opacity = 0;
        }

    }

}

void
draw_cover_art_with_mask(Element *element, cairo_t *ctx, const char *imgpath)
{
    int cover_w=1,cover_h=1;

    cairo_surface_t *cover_surface =
        cairo_image_surface_create_from_png(
        imgpath);
    cover_w = cairo_image_surface_get_width(cover_surface);
    cover_h = cairo_image_surface_get_height(cover_surface);
    cairo_save(ctx);
    cairo_scale(ctx,
                element->w*1./cover_w,
                element->h*1./cover_h);
    cairo_set_source_surface(ctx,
                cover_surface, 
                element->x*cover_w*1./element->w,
                element->y*cover_h*1./element->h);
    
    cairo_paint(ctx);
    cairo_restore(ctx);

    // apply the mask
    cairo_set_source_rgb(ctx,0,0,0);
    cairo_mask_surface(ctx,element->surface,
                element->x,
                element->y);
    cairo_fill(ctx);
}

void
onCurrentCoverArtDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;
    char *center_img_path = getenv("CENTER_COVER_ART");

    if(!center_img_path) return;

    draw_cover_art_with_mask(element,ctx,center_img_path);
}

void
onPrevCoverArtDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;
    char *prev_img_path = getenv("PREV_COVER_ART");

    if(!prev_img_path) return;

    draw_cover_art_with_mask(element,ctx,prev_img_path);
}

void
onNextCoverArtDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;
    char *next_img_path = getenv("NEXT_COVER_ART");

    if(!next_img_path) return;

    draw_cover_art_with_mask(element,ctx,next_img_path);
}


/*
 * Wire the event handlers with the elements
 */

gboolean str_equal(const char *in, const char *ref)
{
   if(!strncmp(in,ref,strlen(ref)) && (strlen(in) == strlen(ref)))
        return TRUE;

   return FALSE;
}

void wire_element(gpointer data, gpointer userdata)
{
    Element *el = (Element *)data;

    if(str_equal(el->name,"prevButton")){
        el->onMouseEnter = onPrevButtonMouseEnter;
        el->onMouseLeave = onPrevButtonMouseLeave;
    } else if(str_equal(el->name,"nextButton")){
        el->onMouseEnter = onNextButtonMouseEnter;
        el->onMouseLeave = onNextButtonMouseLeave;
    } else if(str_equal(el->name,"nextButtonGlow")){
        el->draw = onGlowDraw;
    } else if(str_equal(el->name,"prevButtonGlow")){
        el->draw = onGlowDraw;
    } else if(str_equal(el->name,"currentCoverMask")){
        el->draw = onCurrentCoverArtDraw;
    } else if(str_equal(el->name,"prevCoverMask")){
        el->draw = onPrevCoverArtDraw;
    } else if(str_equal(el->name,"nextCoverMask")){
        el->draw = onNextCoverArtDraw;
    }
}

void wire_logic(GList *elemList)
{
    g_list_foreach(elemList,wire_element,NULL);
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
