
/*
 *
 * Compilation instructions:
 *
 * gcc -I$HOME/include -I/usr/include/libxml2 inkfun.c \
 *      -L/usr/lib64 -lxml2 -o inkfun
 *
 * Valgrind instructions:
 * G_SLICE=always-malloc G_DEBUG=gc-friendly valgrind \
 * --log-file-exactly=inkfun.valgrind \
 * --leak-check=full --leak-resolution=high
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
struct _inkObject_t;

typedef struct _inkObject_t inkObject_t;

struct _inkObject_t{
    char *id;
    char *class;
    unsigned int width;
    unsigned int height;
    inkObject_t *next;
    cairo_surface_t *surface;
    cairo_t *cr;
};

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
        if(p->id) free(p->id);
        if(p->class) free(p->class);

        if(p->cr) cairo_destroy(p->cr);
        if(p->surface) cairo_surface_destroy(p->surface);

        free(p);
    }
}




/*
 * @class inkGui
 */

#define XML_EQUALS(x,y) \
    !(xmlStrcmp((const xmlChar *)x,(const xmlChar *)y))

#define XML_GETATTR(reader,key) \
    xmlTextReaderGetAttribute(reader,(const xmlChar *)key)

struct _inkGui_t{
    RsvgHandle *svgHandle;
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
    int type = 0;
    xmlChar *nodeName = NULL;
    xmlChar *attr = NULL;
    xmlChar *className = NULL;
    xmlChar *idName = NULL;

    /*
     * Create Objects to fill in the parsed SVG data
     */
    inkGui_t *inkGui = NULL;
    ASSERT(inkGui= (inkGui_t *)malloc(sizeof(inkGui_t)))
    memset(inkGui,0,sizeof(inkGui_t));

    while((ret = xmlTextReaderRead(reader)) == 1)
    {
        type = xmlTextReaderNodeType (reader);
        ASSERT(nodeName = xmlTextReaderLocalName(reader))

        if(XML_EQUALS(nodeName,"svg") && 
            (type == XML_READER_TYPE_ELEMENT))
        {
            attr = XML_GETATTR(reader,"width");
            inkGui->width = atoi((char *)attr);
            xmlFree(attr);
            attr = XML_GETATTR(reader,"height");
            inkGui->height = atoi((char *)attr);
            xmlFree(attr);
        }
        xmlFree(nodeName);

        /*
         * If this is not a starting element, ignore it
         * This avoids the cases at the closing anchor of the node
         */
        if (type != XML_READER_TYPE_ELEMENT) continue;

        /*
         * Check if this node is an inkObject element
         * i.e. if it has a class attribute
         */
        if((className = XML_GETATTR(reader,"class")))
        {
            inkObject_t *inkObject = NULL;
            ASSERT(inkObject = new_inkObject())
            inkObject->class = strndup((char *)className,1024);
            xmlFree(className);

            idName = XML_GETATTR(reader,"id");
            inkObject->id = strndup((char *)idName,1024);
            xmlFree(idName);

            /* link the new object in inkGui's inkObject list */
            inkObject->next = inkGui->inkObjectList;
            inkGui->inkObjectList = inkObject;
        }

    }

    xmlFreeTextReader(reader);
    ASSERT(ret == 0)


    /* 
     * Load cairo surfaces from SVG document for each inkObject
     */

    inkObject_t *inkObject;
    char svg_id[64] = "#";
    if(inkGui){
        rsvg_init();
        ASSERT(inkGui->svgHandle = 
            rsvg_handle_new_from_file(svgfilename,NULL))

        inkObject = inkGui->inkObjectList;
        while(inkObject) {
            ASSERT(inkObject->surface = 
                    cairo_image_surface_create(
                        CAIRO_FORMAT_ARGB32,
                        inkGui->width,
                        inkGui->height))
            ASSERT(inkObject->cr = cairo_create(inkObject->surface))

            svg_id[0] = '#';
            svg_id[1] = '\0';
            strncat(svg_id,inkObject->id,64);
            rsvg_handle_render_cairo_sub(
                                inkGui->svgHandle,
                                inkObject->cr,
                                svg_id);
            inkObject = inkObject->next;
        }
    }

    return inkGui;
}

void delete_inkGui(inkGui_t *inkGui)
{
    inkObject_t *inkObject;
    inkObject_t *tmp;

    rsvg_handle_free(inkGui->svgHandle);
    rsvg_term();

    if(inkGui){
        inkObject = inkGui->inkObjectList;
        while(inkObject) {
            tmp = inkObject->next;
            delete_inkObject(inkObject);
            inkObject = tmp;
        }
        free(inkGui);
    }
}

BEGIN_MAIN(1,"inkfun <filename>")

    inkGui_t *inkGui = NULL;
    inkObject_t *inkObject = NULL;

    ASSERT(inkGui = new_inkGui(argv[1]))



    cairo_surface_t *surface = NULL;
    cairo_t *ctx = NULL;

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
                    inkGui->width, inkGui->height,
                    0,
                    WhitePixel(dpy,screen),
                    WhitePixel(dpy,screen)));

    XMapWindow(dpy, win);

    ASSERT(visual = DefaultVisual(dpy,DefaultScreen(dpy)))

    ASSERT(surface =
        cairo_xlib_surface_create(dpy, win, visual, 
                    inkGui->width, inkGui->height));
    ASSERT(ctx = cairo_create(surface));

    /* 
     * Draw inkGui
     */
    inkObject = inkGui->inkObjectList;
    while(inkObject)
    {
        cairo_set_source_surface(ctx,inkObject->surface,0,0);
        cairo_paint(ctx);
        inkObject = inkObject->next;
    }

    XFlush(dpy);
    fflush(stdout);

    //ASSERT(rsvg_handle_close(svgHandle,NULL));

    usleep(3*1000*1000);

    delete_inkGui(inkGui);
    XCloseDisplay(dpy);

END_MAIN


