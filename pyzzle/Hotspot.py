"""
Sprites representing parts of a slide that the user can click.
"""
import pyzzle, media, Text, Slide
import pygame
import os
from pygame.rect import Rect
from pygame.sprite import Sprite
from pygame.font import *
from pygame.locals import *
import standard
from RelativeRect import RelativeRect
from DB import Table,Row

class Hotspot(Sprite):
    """Pygame Sprites representing parts of a slide 
    that the user can click."""
    __metaclass__=Table
    
    cursorDefault  ='fwd.png'
    """The value of the cursor attribute when no other is specified"""
    
    @staticmethod
    def _load(cells):
        row=Row(cells)
        parent  =Slide.Slide[row.parent] if row.parent else None
        link    =Slide.Slide[row.link] if row.link else None
        hotspot=Hotspot(parent, link, 
                       rectRel=RelativeRect((row.left, row.top, row.width, row.height)), 
                       cursor=row.cursor,
                       text=row.text,
                       layer=row.layer,
                       id=row.id,
                       soundfile=row.sound,
                       delay=row.delay)
        if any((row.dragleft,row.dragtop,
                row.dragwidth,row.dragheight)):
            hotspot.drag=RelativeRect((row.dragleft,row.dragtop,
                                       row.dragwidth,row.dragheight))
        if parent:
            parent.add(hotspot)
        if row.transition:
            hotspot.onTransition=getattr(standard, row.transition)
        return hotspot
    def _save(self):
        cells=  \
        {'id':self.id,
         'parent':self.parent.id if self.parent else None,
         'link'  :self.link.id   if self.link   else None,
         'cursor':self.cursor,
         'sound' :self.soundfile,
         'delay' :self.delay,
         'layer' :self._layer,
         'text'  :self.text}
        if 'lambda' not in self.onTransition.__name__:
            cells['transition']=self.onTransition.__name__
        if self._rect:
            rectRel=RelativeRect(self._rect, self.parent.rect)
            for attr in 'left','top','width','height':
                cells[attr]=getattr(rectRel,attr)
        if self.drag:
            for attr in 'left','top','width','height':
                cells['drag'+attr]=getattr(self.drag,attr)
        return cells
    def __init__(self, parent, link, id=None,
                 rectRel=None, layer=0.0, 
                 cursor='', delay=.1,
                 soundfile=None, text=None, drag=None, _template=False,
                 
                 onClick=lambda self: Hotspot.transition(self),
                 onHighlight=lambda self:None,
                 onTransition=standard._noTransition):
        """
        Creates a new Hotspot.
        @param id: A unique identifier for the Hotspot. Used to refer to the Hotspot 
            in scripts and the database
        @param parent: Panel in which the Hotspot resides. 
            Note: This will not add the slide to the panel. You still need to add it
            using Slide.enter() or one of the transition functions
        @param link: Slide the Hotspot will transition to when clicked
        @type rectRel: RelativeRect
        @param rectRel: The relative coordinates representing the area
            that can be clicked. Coordinates are relative to the size of parent.
        @param layer: The layer of the Hotspot. Larger numbers represent upper layers. 
            When the player clicks on an area of the Slide where two Sprites overlap,
            the sprite with the topmost layer is the only one that's activated.
            
        @param cursor: The name of the cursor file that is displayed 
            when no hotspots are highlighted. The default is defined by 
            Panel.cursorDefault. None displays no cursor.
        @param delay: The time that should be taken to transition from parent to link
            when the Hotspot is clicked.
        @param soundfile: The name of the sound file played when the user clicks
            the hotspot.
        @param text: Text that is displayed under the cursor when the user highlights
            the Hotspot.
        @type  drag: RelativeRect 
        @param drag: The relative coordinates of the area the user 
            must drag to activate the hotspot.
        @param _template: Whether the Hotspot is ready made for the Slide. 
            Not intended for use outside the engine
        @param onClick: The function that is called when the Hotspot is clicked.
            If the drag parameter is specified, this function will not be 
            called until the user has dragged the Hotspot to the correct location.
        @param onHighlight: The function that is called when the Hotspot is clicked.
        @param onTransition: The transition function used to transition from 
            parent to link when the Hotspot is clicked.
        """
        if id and not _template:
            Hotspot[id]=self
        Sprite.__init__(self)
        self.id=id
        self.parent=parent
        self._link=link
        self._setLink(link)
        self.rectRel=rectRel
        self._rect=None
        self.cursor=Hotspot.cursorDefault if cursor == '' else cursor
        self.delay=delay
        self._layer=layer
        self.soundfile=soundfile
        self._template=_template
        self.drag=drag
        self.used=False
        self.text=text
        
        self.onClick=onClick
        self.onHighlight=onHighlight
        self.onTransition=onTransition
        
    def _getRect(self):
        """The portion of the screen the user may click to
        activate the Hotspot."""
        if self.rectRel:
            self._rect=self.rectRel.absolute(self.parent.rect)
        return self._rect
    def _setRect(self, rect):  self._rect=rect
    rect=property(_getRect, _setRect)
    
    def _getLink(self):
        """The Panel the user will transition to 
        when the Hotspot is activated"""
        return self._link
    def _setLink(self, slide):
        if hasattr(self._link, 'links'): self._link.links.remove(self)
        self._link=slide
        if hasattr(self._link, 'links'): self._link.links.add(self)
    link=property(_getLink, _setLink)
    

        
    def draw(self,screen):
        """Draws the Hotspot's border, if the game is in design mode. """
        if pyzzle.design and pygame.key.get_mods() & KMOD_SHIFT and not self._template:
            if (self._link or not self._template):
                pygame.draw.rect(screen, pyzzle.Text.Text.colorDefault,
                                 self.rect, 2)
    def highlight(self):
        """Called when the user hovers over the Hotspot.
        Draws cursor and text to the screen, where present, 
        and calls onHighlight"""
        if self.text or (self._link and pyzzle.design):
            text=Text.Text(self._link.id if pyzzle.design else self.text)
            text._getImage()
            textrect=text.rect
            textrect.topleft=pyzzle.cursor.rect.bottomright
            textrect.clamp_ip(pyzzle.screen.get_rect())
            text.draw(pyzzle.screen)
        self.onHighlight(self)
        return self.cursor
        
    def click(self, design=False):
        """Called when the user clicks the Hotspot.
        Plays soundfile and calls onClick. 
        If drag is specified, the user must drag the cursor
        to the drag area in order to call onClick.  
        @param design: Used only for design mode
        """
        if design:
            self.design()
            return
        if pyzzle.design and not self.link:
            return
        
        if self.soundfile:
            media.sounds.load(self.soundfile).play()
            
        activate=not self.drag
        if self.drag:
            rect=self.drag.absolute(self.parent.rect)
            pos=pyzzle.drag()
            activate=rect.collidepoint(pos)
            
        if activate:
            self.onClick(self)
            self.used=True
    def transition(self):
        """Commands the hotspot to transition the user to the link.
        onClick must explicitly call this to transition the user.
        This makes it very easy to script certain behavior, 
        such as for locks."""
        self.onTransition(self.parent, self._link, self.delay)
    

    def design(self, drag=True):
        selected=pyzzle.dragRect(color=(255,0,255)) if drag else Rect(0,0,0,0)
        if selected.width>10 and selected.height>10:
            #add custom hotspot
            hotspotname=pyzzle.promptText("Enter hotspot name: ", 
                                          self.parent.id+self.id if self.id else '')
            if hotspotname and hotspotname not in Hotspot.rows:
                cursorfile=pyzzle.promptText("Enter cursor file: ", Hotspot.cursorDefault)
                if cursorfile:
                    hotspot=Hotspot(parent=self.parent, link=None, 
                                    cursor=cursorfile, id=hotspotname)
                    hotspot.onTransition=standard.transition
                    hotspot.rect=selected
                    self.parent.add(hotspot)
                    hotspot.design(drag=False)
        elif pygame.key.get_mods() & KMOD_CTRL:
            #delete/clear hotspot
            if self._template:
                self._link=None
            else:
                self.kill()
        else:
            #edit hotspot
            slidename=pyzzle.promptText('Enter slide name:')
            if slidename:
                slide=None
                if slidename in Slide.Slide.rows:
                    slide=Slide.Slide[slidename]
                else:
                    slidefile=pyzzle.promptText('Enter slide file:', slidename+'.jpg')
                    if slidefile:
                        slide=Slide.Slide(slidename, slidefile, self.parent.stage)
                        slide._refs={}
                        for ref in 'forward', 'up', 'down', 'right', 'left':
                            slide._refs[ref]=None
                        slide._loadRefs()
                        slide.insert()
                if slide:
                    self._link=slide
                    self.click()