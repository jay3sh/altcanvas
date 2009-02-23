
from inkface.canvas import PygameFace, PygameCanvas

class App:
    GAP = 10
    MAX_TWT_NUM = 5
    index = MAX_TWT_NUM 
    FRAMERATE = 20
    roll = []
    moveflag = False
    def main(self):
        self.canvas = PygameCanvas((800,480),framerate=self.FRAMERATE)
        self.face = PygameFace('data/gui-6.svg')

        self.base_x = self.face.twt0.x
        self.base_y = self.face.twt0.y
        self.base_w = self.face.twt0.svg.w
        self.base_h = self.face.twt0.svg.h

        self.moveStep = self.base_h + self.GAP
        
        for i in range(self.MAX_TWT_NUM):
            self.face.clone('twt0','twt'+str(i+1),
                            new_x = self.base_x,
                            new_y = self.base_y+\
                                ((i+1)*(self.base_h + self.GAP)))

        for i in range(self.MAX_TWT_NUM + 1):
            self.roll.append(self.face.get('twt'+str(i)))
            self.roll[i].onDraw = self.drawTwt

        self.roll[self.index].onDraw = self.doNotDraw
        
        self.face.nextButton.onLeftClick = self.rollToNext

        self.canvas.add(self.face)
        try:
            self.canvas.eventloop()
        except Exception, e:
            print 'Caught '+str(e)

    def drawTwt(self, elem, screen):
        if self.moveflag:
            elem.y -= (self.base_h + self.GAP)/self.FRAMERATE
            self.twtAnimCounter += 1

            if self.twtAnimCounter >= self.MAX_TWT_NUM:
                self.twtAnimCounter = 0
                self.moveAmount -= int(self.moveStep/self.FRAMERATE)
                if self.moveAmount < int(self.moveStep/self.FRAMERATE):
                    self.moveflag = False

        screen.blit(elem.sprite.image,(elem.x,elem.y))

    def doNotDraw(self, elem, screen):
        if self.moveflag:
            elem.y -= (self.base_h + self.GAP)/self.FRAMERATE

    def rollToNext(self):
        self.roll[self.index].onDraw = self.drawTwt
        self.roll[self.index].y = self.base_x + self.MAX_TWT_NUM*self.moveStep
        self.index = (self.index + 1)%(self.MAX_TWT_NUM + 1)
        self.roll[self.index].onDraw = self.doNotDraw

        self.moveAmount = self.moveStep
        self.moveflag = True
        self.twtAnimCounter = 0


App().main()






