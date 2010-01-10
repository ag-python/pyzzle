"""Presents text to the user"""
import os
import media
import pyzzle
from pygame.rect import *
from pygame.sprite import *

class Text(Sprite):
    """Presents text to the user"""
    fontFileDefault='freesansbold.ttf'
    fontSizeDefault=32
    colorDefault=(0,0,0)
    def __init__(self, text, fontFile=None, fontSize=None, color=None,
                 slide=None, rectRel=None, onClick=None, cursor=None):
        """Creates new Text"""
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
        """The coordinates of the movie.
        rect coordinates are determined by rectRel. 
        If a coordinate in rectRel is None, the coordinate is 
        determined by the slide's image size. 
        """
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
        """The image of text as presented to the user"""
        font=media.fonts.load(self.fontFile)
        self.image=font.render(self.text, False, self.color)
        self._getRect()
    def _getImage(self):
        self._loadImage()
        return self.image
    
    def draw(self, screen):
        """Writes the text to the screen"""
        text=self._getImage()
        textrect=self._getRect()
        screen.blit(text, textrect)
    def highlight(self):
        """Called when text is highlighted by the user."""
        if self.cursor:
            pyzzle.cursor.image=media.cursors.load(self.cursor)
    def click(self,*param):
        """Called when user clicks on the text. Runs onClick() function"""
        if self.onClick:
            self.onClick()