import pygame
import sys
import os
import gtk
import cairo
from pygame.locals import *

#FOLDER_PATH = '/media/mmc2/bluebox/photos'
FOLDER_PATH = '/home/jayesh/workspace/photos'

screen = None

def load_image(name, colorkey=None):
    try:
        image = pygame.image.load(name)
    except pygame.error, message:
        print 'Cannot load image:', name
        raise SystemExit, message
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_cairo_image(name):
    
    THUMB_H = 80
    THUMB_W = 80
    tmpfname = '/tmp/publishr-thumb.png'
    
    #image = pygame.image.load(name).convert()
    pixbuf = gtk.gdk.pixbuf_new_from_file(name)
    pixbuf = pixbuf.scale_simple(THUMB_W,THUMB_H,gtk.gdk.INTERP_NEAREST)
    pixbuf.save(tmpfname,'png')
    
        
    #imgstr = pygame.image.tostring(img_thumb,'ARGB')
    #pygame.image.save(img_thumb,tmpfname)
    
    surface = cairo.ImageSurface.create_from_png(tmpfname)
    
    ctx = cairo.Context(surface)
    ctx.move_to(0,0)
    ctx.line_to(10,10)
    ctx.stroke()
    
    pat = cairo.LinearGradient(0.0, 0.0, 1.0, 0.0)
    pat.add_color_stop_rgba( 0, 1, 1, 1, 0 )
    pat.add_color_stop_rgba( 1, 1, 1, 1, 1 )
    ctx.set_source(pat)
    ctx.fill()
    ctx.stroke()
    
    imgbuf = surface.write_to_png(tmpfname)
    
    
    #imgsurf = pygame.image.frombuffer(imgbuf,(THUMB_W,THUMB_H),'RGBA')
    
    return pygame.image.load(tmpfname).convert()
    #return imgsurf

def load_images():
    global screen
    images = []
    if os.path.isdir(FOLDER_PATH):
        files = os.listdir(FOLDER_PATH)
        for f in files:
            if f.lower().endswith('jpg') or  \
                f.lower().endswith('jpeg') or  \
                f.lower().endswith('xcf') or  \
                f.lower().endswith('gif'):
                    images.append(FOLDER_PATH+os.sep+f)
    
    x=20
    y=20
    max_x = 800
    max_y = 480
    for iname in images:
        #img,irect = load_image(iname)
        #img = load_cairo_image(iname)
        #img_thumb = pygame.transform.scale(img,(80,80))
        #img_thumb.set_alpha(100)
        
        img_thumb = load_cairo_image(iname)
        
        screen.blit(img_thumb,(x,y))
        
        pygame.display.flip()
        x = x+15
        y = y+20
        '''
        x = x + 100
        if x >= max_x-100:
            y = y+100
            x = 0
        '''
        
        
                    
                    
def main():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption('Publishr')
    
    ##
    # Setup the white background
    
    background = pygame.Surface(screen.get_size()).convert()
    background.fill((250,250,250))
    screen.blit(background,(0,0))
    pygame.display.flip()
    
    load_images()
    
    while 1:
        event = pygame.event.wait()
        if event.type == QUIT:
            pygame.display.quit()
            sys.exit()
        


if __name__ == '__main__':
    main()