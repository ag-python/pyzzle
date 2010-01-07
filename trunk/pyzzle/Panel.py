
from pygame.sprite import *
from pygame.rect import Rect
import pyzzle, media
import os

class Panel(Sprite):
    """A pygame Sprite that borrows some methods of the pygame Group class.
    This allows Panels to be nested. 
    
    All nested sprites must have the rect attribute."""
    
    cursorDefault='default.png'
    
    def __init__(self):
        self.cursor=Panel.cursorDefault
        
        Sprite.__init__(self)
        self._rect=Rect(0,0,0,0)
        self.sprites=LayeredUpdates()
        
        self.onEnter=lambda x:None
        """The function that is called when the player enters the slide."""
        self.onExit =lambda x:None
        """The function that is called when the player exits the slide."""
    def __iter__(self):
        return self.sprites.__iter__()
    def __contains__(self, sprite):
        return self.sprites.__contains__(sprite)
    
    def _getRect(self):
        return self._rect
    def _setRect(self,rect):
        self._rect=rect
    rect=property(_getRect, _setRect)
    
    def add(self, sprite):
        """Adds the sprite to the Panel. 
        @see: Group.add()
        @note: While this method overrides Sprite.add(),
            it does not perform the same behavior! 
        """
        self.sprites.add(sprite)
        if hasattr(sprite, '_layer'):
            self.sprites.change_layer(sprite, sprite._layer)
    def remove(self, sprite):
        """Removes the sprite from the Panel. 
        @see: Group.add()"""
        self.sprites.remove(sprite)
    def empty(self):
        """Empties all nested sprites from the Panel. 
        @see: Group.empty()"""
        self.sprites.empty()
    def draw(self, screen):
        """Draws nested sprites to the screen. 
        An image attribute or draw(screen) function is 
        needed for nested sprites to render.
        @type screen: Surface
        @param screen: The surface to draw on.
        @see: Group.draw()"""
        for sprite in self.sprites:
            sprite._getRect()
            if hasattr(sprite, 'draw'):
                sprite.draw(screen)
            elif hasattr(sprite, 'image'):
                screen.blit(sprite.image, sprite.rect)
    def highlight(self):
        """Called when the cursor hovers over the Panel.
        Calls the highlight() method of all nested sprites, where present.
        @rtype: string
        @return: The name of the cursor file that must be displayed
        """
        highlighted=None
        for sprite in self.sprites:
            if sprite.rect.collidepoint(pyzzle.cursor.rect.center):
                highlighted=sprite
        if hasattr(highlighted, 'highlight'):
            return highlighted.highlight()
        else:
            return self.cursor
    def click(self, **param):
        """Called when the user clicks the Panel.
        Calls the click() method of the topmost nested sprite under the cursor.
        If no click() method is found, nothing happens."""
        highlighted=None
        for sprite in self.sprites:
            if sprite.rect.collidepoint(pyzzle.cursor.rect.center):
                highlighted=sprite
        if hasattr(highlighted, 'click'):
            highlighted.click(**param)
    def enter(self, oldslide=None, delay=.1):
        """Called when the Panel is presented to the user.
        Calls the enter() method of all nested sprites, where present.
        @type oldslide: Panel
        @param oldslide: The Panel that was previously presented to the user,
            to be replaced by self
        @param delay: The time it should take for oldslide to transition to self
        """
        for sprite in self.sprites:
            if hasattr(sprite, 'enter'):
                sprite.enter(oldslide=None, delay=.1)
    def exit(self, newslide=None, delay=.1):
        """Called when the Panel is removed from the user.
        Calls the exit() method of all nested sprites, where present.
        @type newslide: Panel
        @param newslide: The Panel that self will be replaced with.
        @param delay: The time it should take for self to transition to newslide.
        """
        for sprite in self.sprites:
            if hasattr(sprite, 'exit'):
                sprite.exit(newslide=None, delay=.1)