
/*
 *
 * Compilation instructions:
 *
 * gcc -I$HOME/include -I/usr/include/libxml2 inkfun.c \
 *      -L/usr/lib64 -lxml2 -o inkfun
 *
 */

#include <boiler.h>

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <librsvg/rsvg.h>
#include <librsvg/rsvg-cairo.h>
#include <cairo-xlib.h>


struct {
    

} _inkObject_t;
typedef struct _inkObject_t inkObject_t;

BEGIN_MAIN(1,"inkfun <filename>")

    xmlDoc *doc = NULL;
    xmlNode *root = NULL;
    char *width_str, *height_str;
    int width,height;

    RsvgHandle *svgHandle = NULL;
    cairo_surface_t *surface = NULL, *isurface=NULL;
    cairo_t *ctx = NULL,*ictx=NULL;

    rsvg_init();

    /*
     * Find width and height of complete image
     */
    ASSERT(doc = xmlReadFile(argv[1],NULL,0))

    ASSERT(root = xmlDocGetRootElement(doc))

    ASSERT(width_str = (char*)xmlGetProp(root, (xmlChar*)"width"))
    width = atoi(width_str);
    xmlFree(width_str);
    ASSERT(height_str = (char*)xmlGetProp(root, (xmlChar*)"height"))
    height = atoi(height_str);
    xmlFree(height_str);

    printf("Width = %d, Height = %d\n",width,height);

    /*
     * Create X surface of the size of complete image
     */
    Window win,rwin;
    Display *dpy=NULL;
    int screen = 0;
    Visual *visual = NULL;

    ASSERT(dpy = XOpenDisplay(0));
    ASSERT(rwin = DefaultRootWindow(dpy));
    screen = DefaultScreen(dpy);
    ASSERT(win = XCreateSimpleWindow(
                    dpy,
                    rwin,
                    0, 0,
                    width, height,
                    0,
                    WhitePixel(dpy,screen),
                    WhitePixel(dpy,screen)));

    XMapWindow(dpy, win);

    ASSERT(visual = DefaultVisual(dpy,DefaultScreen(dpy)))

    ASSERT(surface =
        cairo_xlib_surface_create(dpy, win, visual, width,height));
    ASSERT(ctx =
        cairo_create(surface));

    /* 
     * Start parsing the doc
     */
    ASSERT(svgHandle = rsvg_handle_new_from_file(argv[1],NULL))
    
    ASSERT(isurface = 
        cairo_image_surface_create(CAIRO_FORMAT_ARGB32,800,640))
    ASSERT(ictx = cairo_create(isurface))

    rsvg_handle_render_cairo_sub(svgHandle,ictx,"#g5261");

    cairo_set_source_surface(ctx,isurface,0,0);
    cairo_paint(ctx);

    XFlush(dpy);

    cairo_destroy(ictx);
    cairo_surface_destroy(isurface);

    cairo_destroy(ctx);
    cairo_surface_destroy(surface);

    rsvg_handle_free(svgHandle);
    //ASSERT(rsvg_handle_close(svgHandle,NULL));
    rsvg_term();

    usleep(3*1000*1000);

    XCloseDisplay(dpy);

END_MAIN


