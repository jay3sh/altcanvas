

class TwitBox:
    def __init__(self, face, **args):
        '''
        :param face: Face to which elements belong
        :param background_ename: Element name to use as background
        :param text_ename: Element name to set the twit text with
        :param image_ename: [optional] Element name to draw profile image on
        '''
        self.face = face
        self.__dict__.update(args)

        assert self.background_ename is not None and \
                self.text_ename is not None

        self.background_elem = self.face.get(self.background_ename)
        self.text_elem = self.face.get(self.text_ename)
        if self.image_ename is not None:
            self.image_elem = self.face.get(self.image_ename)

        # Calculate relative distances that can be used further
        self.x_margin = self.text_elem.svg.x
        self.y_margin = self.text_elem.svg.y - self.background_elem.svg.y
        self.clone_counter = 0

    def set_text(self, text):
        words = text.split(' ')
        lines = []
        curline = ''
        for word in words:
            if not self._length_check(curline, word):
                lines.append(curline)
                curline = word
            else:
                curline += ' '+word

        lines.append(curline)

        self.text_elem.svg.text = '\n'.join(lines)
        self.text_elem.refresh(svg_reload=True)

        bg_height = self.text_elem.svg.h + 2*self.y_margin
        self.background_elem.svg.set('height',str(bg_height))
        self.background_elem.refresh(svg_reload=True)
                

    def set_position(self, (x,y)):
        self.background_elem.set_position((x,y))
        txt_x, txt_y = self.text_elem.get_position()
        self.text_elem.set_position((x+self.x_margin, y+self.y_margin))
        
    def clone(self):
        assert self.face is not None

        self.clone_counter += 1

        self.face.clone(self.background_ename,
                        self.background_ename+str(self.clone_counter))

        self.face.clone(self.text_ename,
                        self.text_ename+str(self.clone_counter))

        self.face.clone(self.image_ename,
                        self.image_ename+str(self.clone_counter))


        new_twtbox = TwitBox(self.face, 
            background_ename = \
                self.background_ename+str(self.clone_counter),
            text_ename = self.text_ename+str(self.clone_counter),
            image_ename = self.image_ename+str(self.clone_counter))

        # Pass on the relative distances to new object
        new_twtbox.x_margin = self.x_margin
        new_twtbox.y_margin = self.y_margin

        return new_twtbox


    def set_image(self, img):
        pass

    def _length_check(self, line, word):
        self.text_elem.svg.text = line+' '+word
        self.text_elem.refresh(svg_reload=True, sprite_reload=False)
        return (self.text_elem.svg.w < \
            (self.background_elem.svg.w - 2*self.x_margin))
 
    def get_bounding_box(self):
        extents = None
        for elem in (self.background_elem, self.text_elem, self.image_elem):
            e_x, e_y = elem.get_position()
            extents = self.__union(extents, 
                (e_x, e_y, e_x+elem.svg.w, e_y+elem.svg.h))

        bbox = (extents[0],extents[1],extents[2]-extents[0],extents[3]-extents[1])
        return bbox

    def __union(self, extents, new_extents):
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
 
