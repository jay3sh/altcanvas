

import re
import cairo

from inkface.altsvg import \
    TAG_INKSCAPE_LABEL, TAG_G, TAG_TSPAN, TAG_TEXT
from inkface.altsvg.draw import NODE_DRAW_MAP

class Element:
    '''
    An object that corresponds to certain nodes in an SVG document.

    Refer to the algorithm of :func:`inkface.altsvg.VectorDoc.get_elements` \
    to understand which nodes are converted into Element objects.

    .. attribute:: label
    This is the "Label" given to the node in Inkscape 

    '''
    def __init__(self, node, vdoc):
        self.node = node
        self.vdoc = vdoc
        self.defs = vdoc.defs

        self.surface = None
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
                import xml.etree.ElementTree
                # Be more forgiving, as in the case of single line text
                # If current node is not text node, see if any sub-node
                # is a text node.
                if node.tag == TAG_TEXT:
                    text_node = node
                else:
                    text_node = node.find('.//'+TAG_TEXT)

                # A temp scratch surface to calculate height of a line
                tmp_surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32,1,1)
                tmp_ctx = cairo.Context(tmp_surface)

                tchildren = text_node.getchildren()

                # Save position of first tspan element to use later
                old_x, old_y = \
                        (float(tchildren[0].get('x')),
                        float(tchildren[0].get('y')))

                # Keep copy of first tspan element, used in regenerating it
                tchild_attribs = tchildren[0].attrib.copy()

                # Keep copy of text node element, used in regenerating it
                text_node_attribs = text_node.attrib.copy()

                # Clear the text_node element to get rid of children tspans
                text_node.clear()

                # Insert saved attributes into text_node, which also got 
                # cleared above
                for key,val in text_node_attribs.items():
                    text_node.set(key,val)

                # Create a temporary tspan element to calculate height 
                # of single line
                tmp_tspan = xml.etree.ElementTree.Element(
                                    TAG_TSPAN, tchild_attribs)
                tmp_tspan.text = 'text'

                text_node.insert(0,tmp_tspan)

                ex1,ey1,ex2,ey2 = self.raw_render(
                    tmp_ctx, text_node, simulate=True)
                height = ey2 - ey1
                # TODO: hardcode a gap betwn lines which is 30% of height
                height += 0.30 * height
                
                # Again clear the text_node to remove the temp tspan
                text_node.clear()
                # Again insert its saved attributes
                for key,val in text_node_attribs.items():
                    text_node.set(key,val)

                # Now create tspan elements for each line of new text
                txt_lines = value.split('\n')
                i = 0
                for txt_line in txt_lines:
                    # Calculate position of each tspan element using
                    # old_{x,y} and height calculated above
                    attr_dict = {'x':str(old_x),
                                'y':str(old_y+i*height)}
                    tspan_elem = xml.etree.ElementTree.Element(
                                    TAG_TSPAN, attr_dict)
                    tspan_elem.text = txt_line
                    text_node.insert(0,tspan_elem)
                    i += 1

            elif key == 'label':
                node.set(TAG_INKSCAPE_LABEL,value)
            
        else:
            self.__dict__[key] = value

    def set(self, key, value):
        '''
        Modifies the underlying XML node, manipulating its attribute. For \
        this change to take effect :func:`render` needs to be called.

        :param key: Name of the attribute to modify
        :param value: Value to be assigned to the attribute.
        '''
        if self.node is not None:
            self.node.set(key,value)
        else:
            raise Exception('No SVG node present')

    def dup(self, newName):
        '''
        Duplicates the Element. It is done by creating a separate copy of \
        this XML node.

        :param newName: :attr:`label` of new Element is set to this value
        '''
        import xml.etree.ElementTree
        node_str = xml.etree.ElementTree.tostring(self.node)
        new_node = xml.etree.ElementTree.fromstring(node_str)
        new_elem = Element(new_node, self.vdoc)
        new_elem.label = newName
        return new_elem

        
    def scale(self, factor):
        '''
        Scale this element.

        :param factor: Scaling factor. Value >1 will magnify the element, \
        <1 will diminish the element.
        '''
        self.scale_factor = factor

    def add_node(self, node):
        if self.node == None:
            if self.surface == None:
                # This Element instance will be used later on to render
                # nodes later on. Create a surface of the size of whole
                # document. The oncoming nodes can be drawn on it
                self.surface = cairo.ImageSurface(
                    cairo.FORMAT_ARGB32,
                    int(float(self.vdoc.width)),
                    int(float(self.vdoc.height)))
                self.x = 0
                self.y = 0
                self.w = self.surface.get_width()
                self.h = self.surface.get_height()

            ctx = cairo.Context(self.surface)
            ctx.move_to(0,0)

            self.raw_render(ctx, node)


    def render(self, scratch_surface=None):
        '''
        Render this node.
        '''

        # In case of background surface, node is None. For such elements
        # add_node() should be called instead of render().
        # However the high level app won't know what kind of element it
        # is dealing with. So if it calls render() on a background node
        # then we will silently return
        if self.node == None:
            return

        # If there was no old surface to scratch on, create one 
        if scratch_surface == None:
            scratch_surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(float(self.vdoc.width)),
                int(float(self.vdoc.height)))
            
        scratch_ctx = cairo.Context(scratch_surface)
        extents = self.raw_render(scratch_ctx, self.node, simulate=True)
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
 
        self.surface = cairo.ImageSurface(
            cairo.FORMAT_ARGB32, elem_surface_width, elem_surface_height)
        elem_ctx = cairo.Context(self.surface)
        elem_ctx.translate(-ex1,-ey1)

        if self.scale_factor > 0:
            elem_ctx.scale(self.scale_factor,self.scale_factor)

        self.raw_render(elem_ctx, self.node)

        self.x = ex1
        self.y = ey1
        self.w = self.surface.get_width()
        self.h = self.surface.get_height()


    def raw_render(self, ctx, e, simulate=False):
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

        ctx.save()

        extents = None

        transform_matrix = None

        if transform_type == 'translate':
            transform_matrix = cairo.Matrix(1,0,0,1,x0,y0)
        elif transform_type == 'matrix':
            transform_matrix = cairo.Matrix(xx,xy,yx,yy,x0,y0)

        # TODO: /matrix-dup-code

        if transform_matrix:
            ctx.transform(transform_matrix)

        if e.tag == TAG_G:
            for sub_e in e.getchildren():
                new_extents = self.raw_render(ctx, sub_e, simulate)

                if simulate:
                    if new_extents == None:
                        ex1, ey1, ex2, ey2 = (0,0,0,0)
                    else:
                        ex1, ey1, ex2, ey2 = new_extents

                    # The following adjustment is questionable
                    # TODO
                    if transform_matrix:
                        new_extents = \
                            transform_matrix.transform_point(ex1,ey1)+\
                            transform_matrix.transform_point(ex2,ey2)

                    # /TODO

                    extents = self.__union(extents,new_extents)
        else:
            draw = NODE_DRAW_MAP.get(e.tag, None)
            if draw:
                new_extents = draw(ctx, e, self.defs, simulate)
                if simulate:
                    ex1, ey1, ex2, ey2 = new_extents
                    # The following adjustment is questionable
                    # TODO
                    if transform_matrix:
                        new_extents = \
                            transform_matrix.transform_point(ex1,ey1)+\
                            transform_matrix.transform_point(ex2,ey2)
                    # /TODO
                    extents = self.__union(extents,new_extents)
            else:
                #raise Exception("Shape not implemented: "+e.tag)
                print 'Shape not implemented: '+e.tag
                extents = [0, 0, 0, 0]


        ctx.restore()

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
