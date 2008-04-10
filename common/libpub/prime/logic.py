
from libpub.prime.animation import Path

def on_image_click(image):
    #inComing
    pathIn = Path(image)
    (orderIn,imageW) = self.widgetQ.getWidget(image)
    pathIn.add_start(imageW.x,imageW.y,orderIn)
    pathIn.add_stop(ipx,ipy,padOrder)
    pathIn.num_steps = NUM_STEPS 
    pathInPoints = pathIn.get_points()
    
    pathOut = None
    #outGoing
    if self.imageOnPad:
        pathOut = Path(self.imageOnPad.widget)
        pathOut.add_start(ipx,ipy,padOrder)
        pathOut.add_stop(self.imageOnPad.x,self.imageOnPad.y,self.imageOnPad.order)
        pathOut.num_steps = NUM_STEPS
        pathOutPoints = pathOut.get_points()
        
    for i in range(NUM_STEPS):
        if i == 0:
            continue
        
        # Remove old instances of moving image widgets
        self.widgetQ.remove(pathIn.widget)
        if pathOut:
            self.widgetQ.remove(pathOut.widget)
            
        # Add new instances of moving image widgets
        (order,ww) = pathInPoints[i]
        if padOrder == -1:
            self.widgetQ.append(ww)
            padOrder,_ = self.widgetQ.getWidget(ww.widget)
        else:
            self.widgetQ.insert(padOrder,ww)
            
        if pathOut:
            (order,ww) = pathOutPoints[i]
            self.widgetQ.insert(order,ww)
         
            # refresh the surface
            self.__update_surface()

    # Save the imageOnPad
    self.imageOnPad = self.ImageOnPad()
    self.imageOnPad.widget = image
    self.imageOnPad.x = imageW.x
    self.imageOnPad.y = imageW.y
    self.imageOnPad.order = orderIn
