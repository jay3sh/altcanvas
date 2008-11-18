

//-------------------
// OpenGL canvas
//-------------------

static void
canvas_init(
    gl_canvas_t *self,
    int width,
    int height,
    int fullscreen)
{
   glutInit(&argc, argv);
   glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB | GLUT_DEPTH);
   glutInitWindowSize(250, 250);
   glutInitWindowPosition(100, 100);
   glutCreateWindow("inkface");
   init();
   glutDisplayFunc(display);
   glutReshapeFunc(reshape);
   glutKeyboardFunc(keyboard);
}

void canvas_show(canvas_t *self)
{

}

void canvas_refresh(canvas_t *self)
{

}
                    
void canvas_cleanup(canvas_t *self)
{

}
void inc_dirt_count(canvas_t *self, int count)
{
}
 

void dec_dirt_count(canvas_t *self, int count)
{
}

void canvas_draw_elem(canvas_t *self, Element *elem)
{

}

gl_canvas_t *gl_canvas_new(void)
{
    gl_canvas_t *object = NULL;
    ASSERT(object = (gl_canvas_t *)malloc(sizeof(gl_canvas_t)));
    memset(object,0,sizeof(gl_canvas_t));

    object->init = canvas_init;
    object->cleanup = canvas_cleanup;
    object->refresh = canvas_refresh;
    object->show = canvas_show;
    object->inc_dirt_count = inc_dirt_count;
    object->dec_dirt_count = dec_dirt_count;
    object->draw_elem = canvas_draw_elem;
 
    return object;
}
