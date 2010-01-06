import os
import media
import pyzzle
from pygame.rect import *
from pygame.sprite import *

class Text(Sprite):
    fontFileDefault='freesansbold.ttf'
    fontSizeDefault=32
    colorDefault=(0,0,0)
    def __init__(self, text, fontFile=None, fontSize=None, color=None,
                 slide=None, rectRel=None, onClick=None, cursor=None):
        if not fontFile: fontFile=Text.fontFileDefault
        if not fontSize: fontSize=Text.fontSizeDefault
        if not color: color=Text.colorDefault
        Sprite.__init__(self)
        self.slide= slide
        if self.slide: slide.add(self)
        self.text = text
        self.fontFile = fontFile
        self.fontSize = fontSize
        self.image= None
        self.rectRel = rectRel
        self.rect=None
        self.color = color
        self.onClick=onClick
        self.cursor=cursor
    def _getRect(self):
        if self.rectRel:
            slideRect=self.slide.image.get_rect()
            left, top, width, height=self.rectRel
            self.rect=Rect(left   *slideRect.width  +self.slide.rect.left,
                           top    *slideRect.height +self.slide.rect.top,
                           width  *slideRect.width,
                           height *slideRect.height)
        if self.image:
            imagerect=self.image.get_rect()
            if not self.rect:
                self.rect=imagerect
            else:
                self.rect.width=imagerect.width
                self.rect.height=imagerect.height
        return self.rect
    
    def setText(self, text):
        self.text=text
        if self.image:
            self._loadImage()
    
    def _loadImage(self):
        font=media.fonts.load(self.fontFile)
        self.image=font.render(self.text, False, self.color)
        self._getRect()
    def _getImage(self):
        self._loadImage()
        return self.image
    
    def draw(self, screen):
        text=self._getImage()
        textrect=self._getRect()
        screen.blit(text, textrect)
    def highlight(self):
        if self.cursor:
            pyzzle.cursor.image=media.cursors.load(self.cursor)
    def click(self,*param):
        if self.onClick:
            self.onClick()