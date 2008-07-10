
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

#define XML_EQUALS(x,y) \
    !(xmlStrcmp((const xmlChar *)x,(const xmlChar *)y))

#define XML_GETATTR(reader,key) \
    xmlTextReaderGetAttribute(reader,(const xmlChar *)key)


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

inkObject_t *
new_inkObject(
    xmlChar *defs_xml,
    xmlChar *obj_xml)
{
    printf("Inside new_inkObject: %s\n",obj_xml);
    /* manipulate obj_xml */
    xmlTextReader *reader = NULL;
    char *x_str = NULL;
    char *y_str = NULL;
    double x=0,y=0;
    int ret = 0;
    xmlChar *tmpName = NULL;
    ASSERT(reader = xmlReaderForMemory((const char *)obj_xml,
                                strlen((char *)obj_xml),
                                NULL,NULL,0))
    while((ret = xmlTextReaderRead(reader)) == 1){
        ASSERT(tmpName = xmlTextReaderLocalName(reader))
        if(XML_EQUALS(tmpName,"rect"))
        {
            xmlNode *tree = xmlTextReaderExpand(reader);
            /*
            char *attr = NULL;
            int attr_count = xmlTextReaderAttributeCount(reader);
            int i=0;
            for(; i<attr_count; i++){
                attr = xmlTextReaderGetAttributeNo(reader,i);
                if(XML_EQUALS(attr,"x")){
                } else if(XML_EQUALS(attr,"y")){
                } else {
                    printf("%s\n",(char *)attr);
                }
            }
            */
            printf("node %s\n",(char *)tmpName);
            ASSERT(x_str = (char *)XML_GETATTR(reader,"x"))
            ASSERT(y_str = (char *)XML_GETATTR(reader,"y"))
            x = atof(x_str);
            y = atof(y_str);
            printf("x = %f, y = %f \n",x,y);
        }
    }


    /* Create object */
    inkObject_t *p = NULL;
    ASSERT(p = (inkObject_t *)malloc(sizeof(inkObject_t)))
    memset(p,0,sizeof(inkObject_t));

    /*
    xmlBuffer *buf = xmlBufferCreate();
    xmlBufferWriteChar(buf, "<svg>");
    xmlBufferWriteCHAR(buf, defs_xml);
    xmlBufferWriteCHAR(buf, obj_xml);
    xmlBufferWriteChar(buf, "</svg>");

    RsvgHandle *rsvgHandle = rsvg_handle_new_from_data(
          (guint8 *)xmlBufferContent(buf), xmlBufferLength(buf), NULL);
    xmlFree(buf);
    RsvgDimensionData rsvgDim;
    rsvg_handle_get_dimensions(rsvgHandle, &rsvgDim);
    */

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

    xmlChar *defs_xml = NULL;
    xmlChar *obj_xml = NULL;

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

        if(XML_EQUALS(nodeName,"defs") && 
            (type == XML_READER_TYPE_ELEMENT))
        {
            ASSERT(defs_xml = xmlTextReaderReadOuterXml(reader))
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
            ASSERT(obj_xml = xmlTextReaderReadOuterXml(reader))

            inkObject_t *inkObject = NULL;
            ASSERT(inkObject = new_inkObject(defs_xml,obj_xml))
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

cairo_surface_t *test1(char *svgfilename, const char *objname)
{
    int ret = 0;
    int type;
    xmlTextReaderPtr reader = NULL;
    xmlChar *nodeName = NULL;
    xmlChar *className = NULL;
    xmlChar *obj_xml = NULL;
    xmlChar *defs_xml = NULL;
    ASSERT(reader = xmlNewTextReaderFilename(svgfilename))
    
    while((ret = xmlTextReaderRead(reader)) == 1)
    {
        type = xmlTextReaderNodeType (reader);
        ASSERT(nodeName = xmlTextReaderLocalName(reader))
        if((type == XML_READER_TYPE_ELEMENT))
        {
            if(XML_EQUALS(nodeName,"defs")){
                defs_xml = xmlTextReaderReadOuterXml(reader);
            }

            if((className = XML_GETATTR(reader,"class"))){
                xmlChar *idName = NULL;

                idName = XML_GETATTR(reader,"id");
                if(XML_EQUALS(idName,objname)){
                    obj_xml = xmlTextReaderReadOuterXml(reader);
                }
            }
        }
    }

    xmlBuffer *buf = xmlBufferCreate();
    xmlBufferWriteChar(buf, "<svg>");
    xmlBufferWriteCHAR(buf, defs_xml);
    xmlBufferWriteCHAR(buf, obj_xml);
    xmlBufferWriteChar(buf, "</svg>");

    RsvgHandle *rsvgHandle = rsvg_handle_new_from_data(
          (guint8 *)xmlBufferContent(buf), xmlBufferLength(buf), NULL);

    xmlFree(buf);
    RsvgDimensionData rsvgDim;
    rsvg_handle_get_dimensions(rsvgHandle, &rsvgDim);

    printf("w = %d, h = %d\n",rsvgDim.width,rsvgDim.height);
    cairo_surface_t *surface;
    cairo_t *cr;
    surface = cairo_image_surface_create(
                        CAIRO_FORMAT_ARGB32,rsvgDim.width,rsvgDim.height);
                        //CAIRO_FORMAT_ARGB32,800,480);
    cr = cairo_create(surface);
    cairo_set_source_rgb(cr,0.6,0.9,0.8);
    cairo_rectangle(cr,0,0,rsvgDim.width,rsvgDim.height);
    cairo_fill(cr);
    rsvg_handle_render_cairo(rsvgHandle, cr);

    return surface;
}

xmlChar *
eat_xy(xmlChar *str)
{
    char *mod_str = NULL;
    char *tmp = NULL;
    ASSERT(mod_str = malloc(sizeof(char)*xmlStrlen(str)))
    ASSERT(tmp = malloc(sizeof(char)*xmlStrlen(str)))
    xmlNode *node=NULL;
    xmlDoc *doc = xmlParseMemory((const char *)str,xmlStrlen(str));
    for(node=doc->children; node!=NULL; node=node->next){
        sprintf(mod_str,"<%s",(char *)node->name);
        xmlAttr *attrs = node->properties;
        xmlAttr *attr=NULL;
        for(attr = attrs; attr != NULL; attr=attr->next){
            if(strcmp((char *)attr->name,"x")){
                sprintf(tmp,"\n%s=%s",
                    (char *)attr->name,
                    (char *)xmlGetProp(node,attr->name));
                strncat(mod_str,tmp,strlen(tmp));
            }
        }
        strcat(mod_str,"/>");
    }

    xmlBuffer* xbuf = xmlBufferCreate();
    xmlBufferCCat(xbuf,mod_str);
    return xmlBufferContent(xbuf);

}

BEGIN_MAIN(2,"inkfun <filename>")

    printf("answer = %s\n",
        eat_xy("<rect x=\"3434.34343\"\ny=\"4545.432434\"\n/>"));
    exit(0);

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
    cairo_surface_t *isurface = NULL;
    isurface = test1(argv[1],argv[2]);

        cairo_set_source_surface(ctx,isurface,0,0);
        cairo_paint(ctx);
    */

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


