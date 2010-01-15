"""A collection of slides and hotspots that represent 
an object within on/off modes 
"""
import pyzzle
from Slide import Slide
from Hotspot import Hotspot
from DB import Table,Row

class Switch:
    """A collection of slides and hotspots that together represent 
    an object within the game world that has persistant on/off modes 
    (switch, lever, button, etc.) 
    
    @warning: The Switch class is still very early in design, 
    and I reserve the right to radically change as I see fit.
    You have been warned. 
    """
    __metaclass__=Table
    
    
    @staticmethod
    def _load(cells):
        row=Row(cells)
        onslide=Slide[row.onslide] if row.onslide else None
        offslide=Slide[row.offslide] if row.offslide else None
        switches=[]
        if row.onhotspot: switches+=[Hotspot[row.onhotspot]]
        if row.offhotspot: switches+=[Hotspot[row.offhotspot]]
        return Switch(onslide,offslide, switches, on=row.on, id=row.id)
    def __init__(self, onslide, offslide, hotspots, on=False,
                 onSwitch=lambda self:Switch.switch(self), id=None):
        if id: Switch.rows[id]=self
        self.id=id
        self.onslide=onslide
        self.offslide=offslide
        self.hotspots=hotspots
        self.on=on
        self._hotspot=None
        self.onSwitch=onSwitch
        def onClick(hotspot):
            self._hotspot=hotspot
            self.onSwitch(self)
        for hotspot in self.hotspots:
            hotspot.onClick=onClick
            
    def switch(self):
        self.on=not self.on
        if self.onslide != self.offslide and all([self.onslide, self.offslide]):
            oldslide =self.offslide if self.on else self.onslide
            newslide =self.onslide  if self.on else self.offslide
            for link in oldslide.links:
                if link not in self.hotspots:
                    link.link=newslide
            if self._hotspot:
                self._hotspot.transition()