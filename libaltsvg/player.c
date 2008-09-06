#include "rsvg.h"
#include "inkface.h"
#include "string.h"

#define ANIM_LENGTH 6

char *center_img_path;
char *prev_img_path;
char *next_img_path;

typedef enum {PLAYER_PLAY, PLAYER_PAUSE} player_status_t;
player_status_t player_status;

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
    ASSERT(el->on_mouse_over);
    ASSERT(result = g_list_find_custom(
        elemList,el->on_mouse_over,compare_element_by_name)); 
    ASSERT(elmo = (Element *)result->data);

    elmo->opacity = 100;

    signal_paint();
}

void
rotate_cover_art(GList *element_list,gboolean forward)
{
    GList *result;
    Element *currentCover, *prevCover, *nextCover;
    ASSERT(result = g_list_find_custom(
        element_list,"currentCoverMask",compare_element_by_name)); 
    ASSERT(currentCover = (Element *)result->data);
    ASSERT(result = g_list_find_custom(
        element_list,"prevCoverMask",compare_element_by_name)); 
    ASSERT(prevCover = (Element *)result->data);
    ASSERT(result = g_list_find_custom(
        element_list,"nextCoverMask",compare_element_by_name)); 
    ASSERT(nextCover = (Element *)result->data);

    if(currentCover->target_x ||
        currentCover->target_y ||
        nextCover->target_x ||
        nextCover->target_y ||
        prevCover->target_x ||
        prevCover->target_y)
    {
        /* Animation is already in progress */
        return;
    }

    int tmp_order = currentCover->order;
    if(forward){
        currentCover->order = nextCover->order;
        nextCover->order = prevCover->order;
        prevCover->order = tmp_order;

        currentCover->target_x = nextCover->x;
        currentCover->target_y = nextCover->y;
        nextCover->target_x = prevCover->x;
        nextCover->target_y = prevCover->y;
        prevCover->target_x = currentCover->x;
        prevCover->target_y = currentCover->y;
    } else {
        currentCover->order = prevCover->order;
        prevCover->order = nextCover->order;
        nextCover->order = tmp_order;

        currentCover->target_x = prevCover->x;
        currentCover->target_y = prevCover->y;
        prevCover->target_x = nextCover->x;
        prevCover->target_y = nextCover->y;
        nextCover->target_x = currentCover->x;
        nextCover->target_y = currentCover->y;
    }
    sort_elements();
}

/*
 * Event Handlers
 */

/*
 * Input event handlers
 */
void
onNextButtonMouseEnter(Element *el, void *userdata)
{
    rotate_cover_art((GList *)userdata,TRUE);
    toggle_glow(el,(GList *)userdata,TRUE);
    incr_dirt_count(ANIM_LENGTH+1);
}

void
onNextButtonMouseLeave(Element *el, void *userdata)
{
}

void
onPrevButtonMouseEnter(Element *el, void *userdata)
{
    rotate_cover_art((GList *)userdata,FALSE);
    toggle_glow(el,(GList *)userdata,TRUE);
    incr_dirt_count(ANIM_LENGTH+1);
}

void
onPrevButtonMouseLeave(Element *el, void *userdata)
{
}

void 
onCenterCoverArtEnter(Element *el, void *userdata)
{
}

void 
onPrevCoverArtEnter(Element *el, void *userdata)
{
    rotate_cover_art((GList *)userdata,TRUE);
    incr_dirt_count(1);
}

void 
onNextCoverArtEnter(Element *el, void *userdata)
{
    rotate_cover_art((GList *)userdata,FALSE);
    incr_dirt_count(1);
}

void 
onPlayEnter(Element *el, void *userdata)
{
    if(player_status == PLAYER_PAUSE){
        player_status = PLAYER_PLAY;
    }
    incr_dirt_count(1);
}

void 
onPauseEnter(Element *el, void *userdata)
{
    if(player_status == PLAYER_PLAY){
        player_status = PLAYER_PAUSE;
    }
    incr_dirt_count(1);
}

void
onPlayDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;

    if(player_status == PLAYER_PAUSE){
        cairo_set_source_surface(ctx,
            element->surface,element->x,element->y);
        cairo_paint(ctx);
    }
}

void
onPauseDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;

    if(player_status == PLAYER_PLAY){
        cairo_set_source_surface(ctx,
            element->surface,element->x,element->y);
        cairo_paint(ctx);
    }
}


/*
 * Drawing event handlers
 */
void
onGlowDraw(Element *el, void *userdata)
{
    if(el->opacity > 0){
        if(el->opacity == 100){
            /* first frame of animation */
            int op_corr = 100 % (100/ANIM_LENGTH);
            el->opacity -= op_corr;
        }

        cairo_t *ctx = (cairo_t *)userdata;
        cairo_set_source_surface(ctx,el->surface,el->x,el->y);
        cairo_paint_with_alpha(ctx,el->opacity/100.);
        el->opacity -= 100/ANIM_LENGTH;

        if(el->opacity < 0){
            el->opacity = 0;
        }
    }
}


void
draw_cover_art_with_mask(Element *element, cairo_t *ctx, const char *imgpath)
{

    /* Check if animation is triggered */
    if(element->target_x || element->target_y){
        if(element->frame_count == 0){
            /* This is first frame of animation */
            int x_diff = element->target_x - element->x;
            int y_diff = element->target_y - element->y;
            int x_step_tmp = x_diff / ANIM_LENGTH;
            int y_step_tmp = y_diff / ANIM_LENGTH;
            int x_corr = x_step_tmp ? x_diff % x_step_tmp : x_diff;
            int y_corr = y_step_tmp ? y_diff % y_step_tmp : y_diff;

            element->x += x_corr;
            element->y += y_corr;

            element->x_step = (element->target_x - element->x)/ANIM_LENGTH;
            element->y_step = (element->target_y - element->y)/ANIM_LENGTH;

        }
        element->frame_count++;
        element->x += element->x_step;
        element->y += element->y_step;

        if((element->x == element->target_x) && 
            (element->y == element->target_y)){
            /* Animation is complete */
            element->target_x = 0;
            element->target_y = 0;
            element->frame_count = 0;
            element->x_step = 0;
            element->y_step = 0;
        }
    }


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

    if(!center_img_path) return;

    draw_cover_art_with_mask(element,ctx,center_img_path);
}

void
onPrevCoverArtDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;

    if(!prev_img_path) return;

    draw_cover_art_with_mask(element,ctx,prev_img_path);
}

void
onNextCoverArtDraw(Element *element, void *userdata)
{
    cairo_t *ctx = (cairo_t *)userdata;

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
        el->onMouseEnter = onPrevCoverArtEnter;
    } else if(str_equal(el->name,"nextCoverMask")){
        el->draw = onNextCoverArtDraw;
        el->onMouseEnter = onNextCoverArtEnter;
    } else if(str_equal(el->name,"playButton")){
        el->onMouseEnter = onPlayEnter;
        el->draw = onPlayDraw;
    } else if(str_equal(el->name,"pauseButton")){
        el->onMouseEnter = onPauseEnter;
        el->draw = onPauseDraw;
    }
}

void wire_logic(GList *elemList)
{
    g_list_foreach(elemList,wire_element,NULL);
}

void init_app()
{
    player_status = PLAYER_PAUSE;
    center_img_path = g_strdup(getenv("CENTER_COVER_ART"));
    prev_img_path = g_strdup(getenv("PREV_COVER_ART"));
    next_img_path = g_strdup(getenv("NEXT_COVER_ART"));
}

void cleanup_app()
{
    g_free(center_img_path);
    g_free(prev_img_path);
    g_free(next_img_path);
}

int main(int argc, char *argv[])
{

    if(argc < 2){
        printf("%s <svg-filepath>\n",argv[0]);
        exit(0);
    }

    init_backend(argv[1],FALSE);

    init_app();

    GList *element_list = load_element_list();

    wire_logic(element_list);

    fork_painter_thread();

    eventloop();

    cleanup_backend();

    return 0;
}
