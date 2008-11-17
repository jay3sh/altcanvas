
#ifndef __COMMON_H__
#define __COMMON_H__

RsvgHandle *rsvg_handle_from_file(const char *filename);
GList *load_element_list(char *svgname);

typedef struct element_s element_t;

void * painter_thread(void *arg);

#define REFRESH_INTERVAL_MSEC 50

#define POINTER_STATE_TAP       0x1
#define POINTER_STATE_ENTER     0x2
#define POINTER_STATE_LEAVE     0x4

#define DUP_TAP_IGNORANCE_LIMIT 1

int process_motion_event(Element *el,XMotionEvent *mevent);
int calculate_pressure(Element *el, XEvent *event);

#ifdef HAS_XSP

/* device specific data */
#define DEV_X_DELTA 3378
#define DEV_Y_DELTA 3080
#define DEV_X_CORRECTION -300
#define DEV_Y_CORRECTION -454

/**
   translate raw device coordinates to screen coordinates
*/
#define TRANSLATE_RAW_COORDS(x, y) \
{ \
  * x += DEV_X_CORRECTION;\
  * y += DEV_Y_CORRECTION;\
  * x = GLOBAL_WIDTH - (GLOBAL_WIDTH * *x) / DEV_X_DELTA;\
  * y = GLOBAL_HEIGHT - (GLOBAL_HEIGHT * *y) / DEV_Y_DELTA;\
}

#endif /* HAS_XSP */

#endif /* __COMMON_H__ */
