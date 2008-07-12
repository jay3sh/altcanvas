
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

xmlBuffer *
extract_location(xmlChar *str, xmlChar **id,double *loc_x, double *loc_y);

/*
 * @class inkObject
 */
struct _inkObject_t;

typedef struct _inkObject_t inkObject_t;

struct _inkObject_t{
    char *id;
    char *class;
    unsigned int x;
    unsigned int y;
    unsigned int width;
    unsigned int height;
    inkObject_t *next;
    cairo_surface_t *surface;
    cairo_t *cr;
    RsvgHandle *rsvgHandle;
};


inkObject_t *
new_inkObject(
    xmlChar *defs_xml,
    xmlChar *obj_xml)
{
    /* manipulate obj_xml */
    xmlChar *core_obj_xml = NULL;
    xmlBuffer *xbuf = NULL;
    double x=0,y=0;

    /* Create object */
    inkObject_t *p = NULL;
    ASSERT(p = (inkObject_t *)malloc(sizeof(inkObject_t)))
    memset(p,0,sizeof(inkObject_t));

    xmlChar *idName = NULL;
    ASSERT(xbuf = extract_location(obj_xml,&idName,&x,&y))
    ASSERT(core_obj_xml = xmlBufferContent(xbuf))

    p->id = strndup((const char *)idName,64);
    xmlFree(idName);
    p->x = (unsigned int)x;
    p->y = (unsigned int)y;

    xmlBuffer *buf = xmlBufferCreate();
    xmlBufferWriteChar(buf, "<svg>");
    xmlBufferWriteCHAR(buf, defs_xml);
    xmlBufferWriteCHAR(buf, core_obj_xml);
    xmlBufferWriteChar(buf, "</svg>");

    xmlChar *bufc = xmlBufferContent(buf);
    p->rsvgHandle = rsvg_handle_new_from_data(
          (guint8 *)bufc, xmlBufferLength(buf), NULL);
    xmlFree(bufc);
    ASSERT(p->rsvgHandle);

    RsvgDimensionData rsvgDim;
    rsvg_handle_get_dimensions(p->rsvgHandle, &rsvgDim);

    xmlFree(buf);
    xmlBufferFree(xbuf);

    /* Create cairo surface from SVG node */
    ASSERT(p->surface = 
            cairo_image_surface_create(
                CAIRO_FORMAT_ARGB32,
                rsvgDim.width,
                rsvgDim.height))
    ASSERT(p->cr = cairo_create(p->surface))

    char svg_id[64] = "#";
    svg_id[0] = '#';
    svg_id[1] = '\0';
    strncat(svg_id,p->id,64);
    rsvg_handle_render_cairo_sub(
                        p->rsvgHandle,
                        p->cr,
                        svg_id);
    return p;
}

void delete_inkObject(inkObject_t *p)
{
    if(p){
        if(p->id) free(p->id);
        if(p->class) free(p->class);

        if(p->cr) cairo_destroy(p->cr);
        if(p->surface) cairo_surface_destroy(p->surface);

        if(p->rsvgHandle) {
            rsvg_handle_free(p->rsvgHandle);
        }
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

    /*
     * Create Objects to fill in the parsed SVG data
     */
    inkGui_t *inkGui = NULL;
    ASSERT(inkGui= (inkGui_t *)malloc(sizeof(inkGui_t)))
    memset(inkGui,0,sizeof(inkGui_t));

    rsvg_init();

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
            xmlFree(obj_xml);


            /* link the new object in inkGui's inkObject list */
            inkObject->next = inkGui->inkObjectList;
            inkGui->inkObjectList = inkObject;
        }

    }

    if(defs_xml) xmlFree(defs_xml);
    xmlFreeTextReader(reader);
    ASSERT(ret == 0)

    return inkGui;
}

void delete_inkGui(inkGui_t *inkGui)
{
    inkObject_t *inkObject;
    inkObject_t *tmp;

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
    cr = cairo_create(surface);
    cairo_set_source_rgb(cr,0.6,0.9,0.8);
    cairo_rectangle(cr,0,0,rsvgDim.width,rsvgDim.height);
    cairo_fill(cr);
    rsvg_handle_render_cairo(rsvgHandle, cr);

    return surface;
}

xmlBuffer *
extract_location(xmlChar *str, xmlChar **id,double *loc_x, double *loc_y)
{
    char *mod_str = NULL;
    char *tmp = NULL;
    ASSERT(mod_str = malloc(sizeof(char)*xmlStrlen(str)))
    ASSERT(tmp = malloc(sizeof(char)*xmlStrlen(str)))
    xmlNode *node=NULL;
    xmlDoc *doc = xmlParseMemory((const char *)str,xmlStrlen(str));
    for(node=doc->children; node!=NULL; node=node->next)
    {
        sprintf(mod_str,"<%s",(char *)node->name);
        xmlAttr *attrs = node->properties;
        xmlAttr *attr=NULL;
        for(attr = attrs; attr != NULL; attr=attr->next){
            if(!strcmp((char *)attr->name,"x")){
                xmlChar *x_str = NULL;
                ASSERT(x_str = xmlGetProp(node,attr->name));
                *loc_x = atof((const char *)x_str);
                xmlFree(x_str);
                sprintf(tmp," %s=\"%d\"",
                    (char *)attr->name,0);
                strncat(mod_str,tmp,strlen(tmp));
            } else if(!strcmp((char *)attr->name,"y")){
                xmlChar *y_str = NULL;
                ASSERT(y_str = xmlGetProp(node,attr->name));
                *loc_y = atof((const char *)y_str);
                xmlFree(y_str);
                sprintf(tmp," %s=\"%d\"",
                    (char *)attr->name,0);
                strncat(mod_str,tmp,strlen(tmp));
            } else if(!strcmp((char *)attr->name,"id")){
                *id = xmlGetProp(node,attr->name);
            } else {
                xmlChar *prop = xmlGetProp(node,attr->name);
                sprintf(tmp," %s=\"%s\"",
                    (char *)attr->name,
                    (char *)prop);
                xmlFree(prop);
                strncat(mod_str,tmp,strlen(tmp));
            }
        }
        strcat(mod_str,"/>");
    }

    free(tmp);
    xmlFreeDoc(doc);
    xmlBuffer* xbuf = xmlBufferCreate();
    xmlBufferCCat(xbuf,mod_str);
    free(mod_str);
    return xbuf;

}

BEGIN_MAIN(1,"inkfun <filename>")

    inkGui_t *inkGui = NULL;
    inkObject_t *inkO = NULL;


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
    inkO = inkGui->inkObjectList;
    while(inkO)
    {
        cairo_set_source_surface(ctx,inkO->surface,inkO->x,inkO->y);
        cairo_paint(ctx);
        inkO = inkO->next;
    }


    XFlush(dpy);
    fflush(stdout);

    //ASSERT(rsvg_handle_close(svgHandle,NULL));

    usleep(3*1000*1000);

    cairo_destroy(ctx);
    cairo_surface_destroy(surface);

    delete_inkGui(inkGui);
    XCloseDisplay(dpy);

END_MAIN


