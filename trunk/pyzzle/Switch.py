import pyzzle
from Slide import slides
from Hotspot import hotspots
from DB import Table

switches=Table()
class Switch:
    @staticmethod
    def _load(row):
        onslide=slides[row.onslide] if row.onslide else None
        offslide=slides[row.offslide] if row.offslide else None
        switches=[]
        if row.onhotspot: switches+=[hotspots[row.onhotspot]]
        if row.offhotspot: switches+=[hotspots[row.offhotspot]]
        return Switch(onslide,offslide, switches, on=row.on, id=row.id)
    def __init__(self, onslide, offslide, hotspots, on=False,
                 onSwitch=lambda self:Switch.switch(self), id=None):
        if id: switches[id]=self
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