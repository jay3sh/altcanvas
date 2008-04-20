
# This file is part of AltCanvas.
#
# http://code.google.com/p/altcanvas
#
# AltCanvas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# AltCanvas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with AltCanvas.  If not, see <http://www.gnu.org/licenses/>.



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
