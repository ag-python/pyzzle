"""A Rect style object whose coordinates are given
as a fraction of another rect's width and height"""
from pygame.rect import Rect

class RelativeRect:
    """A Rect style object whose coordinates are given
    as a fraction of another rect's width and height
    
    Pygame uses the Rect class to store rectangular coordinates.
    One problem with this representation is that coordinates are measured in pixels.
    This presents problems in a Myst game - what if you want to adjust the resolution
    of your image files? Using only rect, you would have to re-adjust the rects of the
    Hotspots inside that slide.
    
    The RelativeRect addresses this ploblem. It stores coordinates as 
    a fraction of another rect's width and height. In our example, the Hotspot's 
    coordinates would be stored as a fraction of the rect from the Slide in which it
    resides. 
    """
    def __init__(self, rect, reference=None):
        """Creates a RelativeRect
        @type rect: Rect or (float,float,float,float)
        @param rect: The Rect that output will represent, or a tuple 
            (left,top,width,height) representing relative coordinates 
            of this instance. 
        @type reference: Rect
        @param reference: the Rect that the instance will be in relation to.
            This parameter is required if a Rect is supplied in the previous
            parameter.
        """
        if reference:
            self.left   =float(rect.left-reference.left) / reference.width
            self.top    =float(rect.top- reference.top)  / reference.height
            self.width  =float(rect.width)               / reference.width
            self.height =float(rect.height)              / reference.height
        else:
            self.left,self.top,self.width,self.height = rect
            
        for coordinate in 'left', 'top', 'width', 'height':
            if not getattr(self,coordinate):
                setattr(self,coordinate,0)
        
    def absolute(self, reference):
        """Gets a pygame Rect that is equivalent to RelativeRect
        when in relation to another Rect.
        
        @type reference: Rect
        @param reference: the Rect that output will be in relation to
        @rtype: Rect
        """
        return Rect(self.left   *reference.width  +reference.left,
                    self.top    *reference.height +reference.top,
                    self.width  *reference.width,
                    self.height *reference.height)