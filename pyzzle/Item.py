import pyzzle
from pyzzle.Slide import Slide, slides
from pyzzle.Hotspot import Hotspot, hotspots
from pyzzle.Panel import Panel
from pygame.sprite import Group
from pygame.rect import Rect
from RelativeRect import RelativeRect
from DB import Table
import standard

items=Table()
class Item:
    inventory=Group()
    @staticmethod
    def _load(row):
        gameSlide=slides[row.gameslide] if row.gameslide else None
        gameHotspot=hotspots[row.gamehotspot] if row.gamehotspot else None
        menuSlide=slides[row.menuslide] if row.menuslide else None
        closeupSlide=slides[row.closeupslide] if row.closeupslide else None
        
        item=Item(gameSlide, gameHotspot, row.takenfile,
                  menuSlide, closeupSlide, id=row.id, taken=row.taken)
        
        return item
    def __init__(self, 
                 gameSlide, gameHotspot, takenfile,
                 menuSlide, closeupSlide=None,
                 id=None, taken=False, 
                 onTake=lambda item:None, onUse=lambda item:None):
        if id: items[id]=self
        
        self.menuSlide=menuSlide
        if menuSlide:
            self.menuHotspot=Hotspot(self.menuSlide, None, onClick=self.use,
                                cursor='grab.png', rectRel=RelativeRect((0,0,1,1)))
            self.menuSlide.add(self.menuHotspot)
        
        
        self.closeupSlide=closeupSlide
        if self.closeupSlide:
            self.closeupPanel=Panel()
            self.closeupPanel._layer=11
            self.closeupPanel.rect=pyzzle.screen.get_rect()
            self.closeupHotspot=Hotspot(self.closeupSlide, None, onClick=self.exit,
                                   cursor='fwd.png', layer=-1)
            self.closeupHotspot.rect=pyzzle.screen.get_rect()
            self.closeupSlide.parent=self.closeupPanel
            self.closeupSlide._getRect()
        
        
        self.gameSlide=gameSlide
        if type(gameHotspot) == Hotspot:
            self.gameHotspot=gameHotspot
        else:
            self.gameHotspot=Hotspot(self.gameSlide, None, rectRel=gameHotspot)
        self.gameHotspot.cursor='grab.png'
        self.gameHotspot.onClick=self.take
        self.gameHotspot.parent=self.gameSlide
        self.takenfile=takenfile
        
        self.taken=taken
        if taken and self.menuSlide:
            self.inventory.add(self.menuSlide)
        elif gameSlide:
            gameSlide.add(self.gameHotspot)
            
        self.onUse=onUse
        self.onTake=onTake
    def add(self):
        if self.gameSlide and self.takenfile:
            self.gameSlide.remove(self.gameHotspot)
            self.gameSlide.file = self.takenfile
        if self.menuSlide:
            self.inventory.add(self.menuSlide)
        self.taken=True
        self.onTake(self)
    def take(self, *param):
        self.add()
        if self.closeupSlide:
            self.use()
    def exit(self, *param):
        if self.menuSlide:
            self.inventory.add(self.menuSlide)
        self.closeupPanel.empty()
        pyzzle.scrollUp(oldslide=self.closeupPanel, newslide=None, delay=.1)
    def use(self, *param):
        self.onUse(self)
        if self.closeupSlide:
            self.drop()
            self.closeupPanel.add(self.closeupSlide)
            self.closeupPanel.add(self.closeupHotspot)
            pyzzle.scrollDown(oldslide=None, newslide=self.closeupPanel, delay=.1)
    def drop(self):
        if self.menuSlide:
            self.inventory.remove(self.menuSlide)