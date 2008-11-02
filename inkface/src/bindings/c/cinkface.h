
GList *inkface_loadsvg(char *svgname);

typedef void (*on_timer_func_t) (void);

typedef struct {
    canvas_t *cobject;

    GList *element_list;
    unsigned int timer_step;

    on_timer_func_t onTimer;

} Canvas_t;


