import sys
from inkface.evas import ECanvas, EFace

class App:
    def main(self):
        try:
            self.face = EFace(sys.argv[1])
        
            canvas = ECanvas((self.face.svg.width,self.face.svg.height))
        
            self.face.load_elements(canvas)
        

            for i in range(26):
                keyChr = chr(ord('A')+i)
                smlKey = self.face.get('key'+keyChr)
                smlKey.onLeftClick = self.onLeftClick
    
                self.face.clone('key'+keyChr, 'key'+keyChr+'med')
                self.face.clone('key'+keyChr, 'key'+keyChr+'big')
    
                medKey = self.face.get('key'+keyChr+'med')
                bigKey = self.face.get('key'+keyChr+'big')

                #medKey = smlKey.dup('key'+keyChr+'med')
                #bigKey = smlKey.dup('key'+keyChr+'big')
    
                medKey.svg.scale(1.5)
                bigKey.svg.scale(2)
    
                medKey.refresh(svg_reload=True)
                bigKey.refresh(svg_reload=True)
    
                smlKey_x,smlKey_y = smlKey.get_position()
                medKey_x,medKey_y = medKey.get_position()
                bigKey_x,bigKey_y = bigKey.get_position()
    
                medKey_x = smlKey_x + smlKey.svg.w/2 - medKey.svg.w/2
                medKey_y = smlKey_y - 30
                medKey.set_position((medKey_x,medKey_y))
                medKey.refresh(svg_reload=False)
    
                bigKey_x = smlKey_x + smlKey.svg.w/2 - bigKey.svg.w/2
                bigKey_y = smlKey_y - 70
                bigKey.set_position((bigKey_x,bigKey_y))
                bigKey.refresh(svg_reload=False)

                medKey.hide()
                bigKey.hide()
    

            canvas.eventloop()
        except KeyboardInterrupt, ki:
            sys.exit(0)

    def doDraw(self, elem):
        if elem.visibility_counter > 0:
            elem.visibility_counter -= 1
        else:
            elem.hide()
            elem.onDraw = None

            if elem.svg.label.endswith('med'):
                bigkeyLabel = elem.svg.label.replace('med','big')
                bigKey = self.face.get(bigkeyLabel)
                bigKey.visibility_counter = 2
                bigKey.onDraw = self.doDraw
                bigKey.unhide()

            return False

        return True
   
    def onLeftClick(self, elem):
        medkeyLabel = elem.svg.label+'med'
        medKey = self.face.get(medkeyLabel)
        medKey.onDraw = self.doDraw
        medKey.unhide()
        medKey.visibility_counter = 2
        
App().main()
