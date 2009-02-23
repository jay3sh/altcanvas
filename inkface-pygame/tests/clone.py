
from inkface.canvas import PygameFace, PygameCanvas

class App:
    def main(self):
        self.canvas = PygameCanvas((800,480))
        self.face = PygameFace('data/gui-5.svg')

        self.face.clone('newsFlash','newsFlash2',new_x=50,new_y=200)

        self.face.newsFlash2.svg.text = 'Any colorful news?!'
        self.face.newsFlash2.refresh(svg_reload=True)
        
        
        self.canvas.add(self.face)
        self.canvas.eventloop()




App().main()






