#include <inkface.h>

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xatom.h>
#include <X11/extensions/Xv.h>
#include <X11/extensions/Xvlib.h>
#include <X11/extensions/XShm.h>
#include <X11/keysym.h>
#include <X11/keysymdef.h>


#define DEPTH 16 

int main(int argc, char *argv[])
{
    Display *dpy=NULL;
    Window window;
    int screen = 0;
    GC gc;
    int ret;
    int	xv_port = -1;
    int	xres,yres;
    XVisualInfo				vinfo;
    XSetWindowAttributes	xswa;

	ASSERT(dpy = XOpenDisplay(NULL));

	screen = DefaultScreen(dpy);

	ASSERT(XMatchVisualInfo(dpy, screen, DEPTH, TrueColor, &vinfo));

	xres   = ScreenOfDisplay (dpy, DefaultScreen(dpy))->width;
	yres   = ScreenOfDisplay (dpy, DefaultScreen(dpy))->height;

	xswa.colormap =  XCreateColormap(dpy, DefaultRootWindow(dpy), vinfo.visual, AllocNone);
	xswa.event_mask = StructureNotifyMask | ExposureMask;
	xswa.background_pixel = 0;
	xswa.border_pixel = 0;


	window = XCreateWindow(dpy, DefaultRootWindow(dpy),
			 0, 0,
			 800,
			 480,
			 0, vinfo.depth,
			 InputOutput,
			 vinfo.visual,
			 CWBackPixel | CWBorderPixel | CWColormap | CWEventMask, 
			 &xswa);

 	XSelectInput(dpy, window, 	
			   KeyPressMask | 
			   KeyReleaseMask | 
			   ButtonPressMask |
			   ButtonReleaseMask
			   ); 

	XMapWindow(dpy, window);
    
	gc = XCreateGC(dpy, window, 0, 0);		

    /*
     * Xv
     */

    XvImageFormatValues *fo;
    int formats;
    int	p_num_adaptors = 0;
    XvAdaptorInfo		*ai = NULL;
    typedef enum { xv_NOFORMAT, xv_RGB, xv_YUV} xvfmt_t;
    xvfmt_t     xvFormat;
    int i=0;

	ret = XvQueryAdaptors(dpy, DefaultRootWindow(dpy), &p_num_adaptors, &ai);  
	ASSERT(ret == Success);

	ASSERT(p_num_adaptors); 

    ASSERT(ai);

	xv_port = ai[0].base_id;
	XvFreeAdaptorInfo(ai);

	fo = XvListImageFormats(dpy, xv_port, &formats);
	for (xvFormat = xv_NOFORMAT, i = 0; i < formats; i++)
	{
		printf("fo[%d]={'%.4s', %s, %s, bpp=%d, %s, planes=%d\n",
			i, (char*)&fo[i].id,
			fo[i].type==XvRGB?"XvRGB":"XvYUV",
			fo[i].byte_order==LSBFirst?"LSBFirst":"MSBFirst",
			fo[i].bits_per_pixel,
			fo[i].format==XvPacked ? "XvPacked" : "XvPlanar",
			fo[i].num_planes);
		if (fo[i].type==XvRGB)
			printf("depth=%d, masks={0x%x,0x%x,0x%x}\n",
				fo[i].depth,
				fo[i].red_mask,
				fo[i].green_mask,
				fo[i].blue_mask);
		else
			printf("bits=[%d,%d,%d], hperiod=[%d,%d,%d], vperiod=[%d,%d,%d], order=\"%s\", %s\n",
				fo[i].y_sample_bits,
				fo[i].u_sample_bits,
				fo[i].v_sample_bits,
				fo[i].horz_y_period,
				fo[i].horz_u_period,
				fo[i].horz_v_period,
				fo[i].vert_y_period,
				fo[i].vert_u_period,
				fo[i].vert_v_period,
				fo[i].component_order,
				fo[i].scanline_order==XvTopToBottom?"XvTopToBottom":"XvBottomToTop");

    /*
		if (fo[i].id != FOURCC_YV12 && fo[i].id != FOURCC_I420)
			continue;
		xvFormat = xv_YUV;
		xvFmtInfo = fo[i];
		break;
    */
	}

	ASSERT(xv_port != -1);

	ASSERT(XShmQueryExtension(dpy));


}
