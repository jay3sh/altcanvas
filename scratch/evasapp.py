
#!/usr/bin/python
import ecore, ecore.evas
import evas

import cairo

def main():
    ee = ecore.evas.SoftwareX11(w=800, h=480)

    canvas = ee.evas

    bg = canvas.Rectangle(color=(255, 255, 255, 255), size=canvas.size)
    bg.show()

    # create cairo surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 100, 100)
    ctx = cairo.Context(surface)
    ctx.rectangle(10,10,80,80)
    ctx.set_source_rgba(1.0,0.0,0.0,0.25)
    ctx.fill()

    w, h = surface.get_width(),surface.get_height()

    img2 = canvas.Image()
    img2.alpha_set(True)
    img2.image_size_set(w, h)
    img2.fill_set(0, 0, w, h)
    img2.image_data_set(surface.get_data())
    img2.resize(w, h)

    img2.show()

    ee.show()

    ecore.main_loop_begin()

if __name__ == '__main__':
    main()
