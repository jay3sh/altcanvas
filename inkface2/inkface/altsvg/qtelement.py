

import re

from inkface.altsvg import \
    TAG_INKSCAPE_LABEL, TAG_G, TAG_TSPAN, TAG_TEXT
from inkface.altsvg.qtdraw import NODE_DRAW_MAP

from PyQt4.QtGui import QPixmap, QPainter, QMatrix, QTransform
from PyQt4.QtCore import Qt

class QtElement:
    def __init__(self, node, vdoc):
        self.node = node
        self.vdoc = vdoc
        self.defs = vdoc.defs

        self.pixmap = None
        self.x, self.y, self.w, self.h = (0, 0, 0, 0)
        self.scale_factor = -1

    def __getattr__(self,key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            node = None
            if self.__dict__.has_key('node'):
                node = self.__dict__['node']

            if node == None:
                raise AttributeError('Unknown attribute: '+key)
                
            if key == 'label' and \
                node.attrib.has_key(TAG_INKSCAPE_LABEL):
                return node.attrib.get(TAG_INKSCAPE_LABEL)
            elif key == 'text':
                tspan = node.find('.//'+TAG_TSPAN)
                if tspan != None: 
                    return tspan.text
            elif self.node.attrib.has_key(key):
                return node.attrib.get(key)

        raise AttributeError('Unknown attribute: '+key)

    def __setattr__(self,key,value):
        # Search into the SVG node for the key
        if key == 'text' or key == 'label':
            if self.__dict__.has_key('node'):
                node = self.__dict__['node']
            else:
                raise Exception('node member is not set')

            if key == 'text':
                # TODO
                raise Exception('Not implemented')
 
        else:
            self.__dict__[key] = value

    def set(self, key, value):
        # TODO
        raise Exception('Not implemented')

    def dup(self, newName):
        # TODO
        raise Exception('Not implemented')

    def scale(self, factor):
        self.scale_factor = factor


    def add_node(self, node):
        if self.node == None:
            if self.pixmap == None:
                # This Element instance will be used later on to render
                # nodes later on. Create a surface of the size of whole
                # document. The oncoming nodes can be drawn on it
                self.pixmap = QPixmap(
                            int(self.vdoc.width),int(self.vdoc.height))
                self.pixmap.fill(Qt.transparent)
                self.x = 0
                self.y = 0
                self.w = self.pixmap.width()
                self.h = self.pixmap.height()

            painter = QPainter()

            painter.begin(self.pixmap)

            self.raw_render(painter, node)

            painter.end()


    def render(self, scratch_pixmap=None):
        # In case of background surface, node is None. For such elements
        # add_node() should be called instead of render().
        # However the high level app won't know what kind of element it
        # is dealing with. So if it calls render() on a background node
        # then we will silently return
        if self.node is None:
            return

        # If there was no old surface to scratch on, create one 
        if self.pixmap == None:
            self.pixmap = QPixmap(
                        int(self.vdoc.width),int(self.vdoc.height))
            self.pixmap.fill(Qt.transparent)
            self.x = 0
            self.y = 0
            self.w = self.pixmap.width()
            self.h = self.pixmap.height()

        painter = QPainter()
        painter.begin(self.pixmap)
        extents = self.raw_render(painter, self.node, simulate=True)
        if extents == None:
            # There can be empty group nodes, hence no extents were returned
            # easy way to deal with them is to create surface of smallest
            # positive dimension on which nothing will be drawn
            # TODO: this might be handled in better way
            ex1, ey1, ex2, ey2 = (0, 0, 1, 1)
        else:
            ex1, ey1, ex2, ey2 = extents

        if self.scale_factor > 0:
            ex1,ey1,ex2,ey2 = \
                map(lambda x: x*self.scale_factor,(ex1,ey1,ex2,ey2))

        if (ex2-ex1) < 0 or (ey2-ey1) < 0:
            raise Exception('Invalid surface dim for %s: %f,%f'%\
                (self.node.get('id'),(ex2-ex1),(ey2-ey1)))

        # This handles cases for empty text elements
        if (ex2-ex1) == 0:
            elem_surface_width = 1
        else:
            elem_surface_width = int(ex2-ex1)

        if (ey2-ey1) == 0:
            elem_surface_height = 1
        else:
            elem_surface_height = int(ey2-ey1)
 
        painter.end()

        self.pixmap = QPixmap(elem_surface_width, elem_surface_height)
        self.pixmap.fill(Qt.transparent)
        elem_painter = QPainter()
        elem_painter.begin(self.pixmap)

        elem_painter.translate(-ex1, -ey1)

        if self.scale_factor > 0:
            elem_painter.scale(self.scale_factor, self.scale_factor)

        self.raw_render(elem_painter, self.node)

        self.x, self.y, self.w, self.h = \
            (ex1, ey1, self.pixmap.width(), self.pixmap.height())

        elem_painter.end()

    def raw_render(self, painter, e, simulate=False):
        ''' render individual SVG node '''
        x0 = None
        y0 = None
        transform = e.attrib.get('transform')

        # TODO: matrix-dup-code
        transform_type = None
        if transform is not None:
            transform = transform.replace(' ','')
            pattern = '(\w+)\s*\(([e0-9-.,]+)\)'
            m = re.search(pattern, transform)
            if m: 
                transform_type = m.group(1)
                transform_values = m.group(2)

                if transform_type == 'translate':
                    x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
                elif transform_type == 'matrix':
                    xx, xy, yx, yy, x0, y0 = \
                    map(lambda x: float(x), transform_values.split(','))
            else:
                raise Exception('Unable to match transform')

        painter.save()

        extents = None

        transform_matrix = None
        if transform_type == 'translate':
            transform_matrix = QMatrix(1, 0, 0, 1, x0, y0)
        elif transform_type == 'matrix':
            transform_matrix = QMatrix(xx, xy, yx, yy, x0, y0)

        if transform_matrix is not None:
            painter.setTransform(QTransform(transform_matrix), True)

        if e.tag == TAG_G:
            for sub_e in e.getchildren():
                new_extents = self.raw_render(painter, sub_e, simulate)

                if simulate:
                    if new_extents is None:
                        ex1, ey1, ex2, ey2 = (0,0,0,0)
                    else:
                        ex1, ey1, ex2, ey2 = new_extents

                    # TODO transform
                    if transform_matrix is not None:
                        new_extents = \
                            transform_matrix.map(ex1,ey1) + \
                            transform_matrix.map(ex2,ey2)

                    extents = self.__union(extents, new_extents) 

        else:
            draw = NODE_DRAW_MAP.get(e.tag, None)
            if draw:
                new_extents = draw(painter, e, self.defs, simulate)
                if simulate:
                    ex1, ey1, ex2, ey2 = new_extents
                    # TODO transform
                    if transform_matrix is not None:
                        new_extents = \
                            transform_matrix.map(ex1,ey1) + \
                            transform_matrix.map(ex2,ey2)
 
                    extents = self.__union(extents,new_extents)
            else:
                raise Exception("Shape not implemented: "+e.tag)

        painter.restore()

        if simulate:
            return extents

    # TODO: extent-union dup code
    def __union(self, extents,new_extents):
        if not extents:
            return new_extents

        ox1,oy1,ox2,oy2 = extents
        nx1,ny1,nx2,ny2 = new_extents

        if nx1 < ox1:
            x1 = nx1
        else:
            x1 = ox1

        if ny1 < oy1:
            y1 = ny1
        else:
            y1 = oy1

        if nx2 > ox2:
            x2 = nx2
        else:
            x2 = ox2

        if ny2 > oy2:
            y2 = ny2
        else:
            y2 = oy2

        return (x1, y1, x2, y2)
    # TODO: /extent-union dup code
