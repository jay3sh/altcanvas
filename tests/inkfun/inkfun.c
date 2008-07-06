
/*
 *
 * Compilation instructions:
 *
 * gcc -I$HOME/include -I/usr/include/libxml2 inkfun.c \
 *      -L/usr/lib64 -lxml2 -o inkfun
 *
 */

#include <boiler.h>

#include <string.h>
#include <unistd.h>

#include <libxml/parser.h>
#include <libxml/tree.h>
#include <libxml/xmlreader.h>
#include <librsvg/rsvg.h>
#include <librsvg/rsvg-cairo.h>
#include <cairo-xlib.h>


/*
 * @class inkObject
 */

struct _inkObject_t{
    xmlChar *id;
    unsigned int width;
    unsigned int height;
    struct _inkObject_t *next;
};
typedef struct _inkObject_t inkObject_t;

inkObject_t *new_inkObject()
{
    inkObject_t *p = NULL;
    ASSERT(p = (inkObject_t *)malloc(sizeof(inkObject_t)))
    memset(p,0,sizeof(inkObject_t));
    return p;
}

void delete_inkObject(inkObject_t *p)
{
    if(p){
        if(p->id) xmlFree(p->id);
        free(p);
    }
}




/*
 * @class inkGui
 */

#define XMLSTR_EQUALS(x,y) \
    !(xmlStrcmp((const xmlChar *)x,(const xmlChar *)y))

struct _inkGui_t{
    unsigned int width;
    unsigned int height;
    inkObject_t *inkObjectList;
};

typedef struct _inkGui_t inkGui_t;

inkGui_t *new_inkGui(const char *svgfilename)
{
    /*
     * Parse the SVG file
     */
    if(!svgfilename) return NULL;

    xmlTextReaderPtr reader = NULL;
    ASSERT(reader = xmlNewTextReaderFilename(svgfilename))

    int ret = 0;
    xmlChar *nodeName = NULL;
    xmlChar *attr = NULL;

    while((ret = xmlTextReaderRead(reader)) == 1)
    {
        ASSERT(nodeName = xmlTextReaderLocalName(reader))
        if(XMLSTR_EQUALS(nodeName,"svg"))
        {
            attr = xmlTextReaderGetAttribute(reader,(const xmlChar *)"width");
            printf("width %s\n",attr);
            xmlFree(attr);
            attr = xmlTextReaderGetAttribute(reader,(const xmlChar *)"height");
            printf("height %s\n",attr);
            xmlFree(attr);
        }
        xmlFree(nodeName);

    }


    xmlFreeTextReader(reader);
    ASSERT(ret == 0)


    /* 
     * Create objects out of parsed SVG XML 
     */
    inkGui_t *p = NULL;
    ASSERT(p= (inkGui_t *)malloc(sizeof(inkGui_t)))

    return p;
}

void delete_inkGui(inkGui_t *inkGui)
{
    if(inkGui){
        //TODO: cleanup inkObject list
        free(inkGui);
    }
}

BEGIN_MAIN(1,"inkfun <filename>")

    new_inkGui(argv[1]);

#if 0
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

    rsvg_handle_render_cairo_sub(svgHandle,ictx,"#g5266");
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
#endif

END_MAIN


