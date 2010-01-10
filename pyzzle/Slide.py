"""
The basic building blocks of myst games. 
Start here if you're not sure where to go
"""
import pygame, os
from pygame.sprite import Group
from pygame.rect import Rect
from pygame.surface import Surface
from RelativeRect import RelativeRect
from Hotspot import Hotspot
from Panel import Panel
from DB import Table,Row
import pyzzle
import standard
import Text
import media

class Slide(Panel):
    """The basic building blocks of myst games.
    
    A typical slide represents a location the player can visit in the game world.
    Some slides may also represent items or switches that the player can interact with.  
    
    Every Slide has its own image file in the game world. 
    When the player encounters the Slide, he is presented with this image. 
    The player clicks on parts of the slide in order to perform certain actions.
    These parts of the slide are called Hotspots.
    
    As a subclass of Panel, the Slide class resembles both the Sprite and Group 
    classes of Pygame. As Sprites, they can blit an image to the screen, but as
    Groups, they can manage the behavior of other Sprites that are nested within them.
    Typically, Hotspots are the only Sprites nested within Slides, but it is possible
    to store other types of Sprites, such as Text, Movies, and even other Slides."""
    
    __metaclass__=Table
    
    @staticmethod
    def _load(cells):
        row=Row(cells)
        stage=pyzzle.stages[row.stage] if row.stage else None
        slide=Slide(row.id, row.image, stage, ambiencefile=row.ambientSound, 
                    layer=row.layer, dialog=row.dialog)
        slide._movementSoundfile=row.movementSound
        slide.rectRel=RelativeRect((row.rectleft, row.recttop, 
                                    row.rectheight, row.rectwidth))
        slide._refs={}
        if stage and stage.movementSound and not row.movementSound:
            slide._movementSoundfile=stage.movementSound
        for ref in 'forward', 'up', 'down', 'right', 'left':
            slide._refs[ref]=row[ref]
        return slide
    def _loadRefs(self):
        rectRels=\
        {'left':    (0,0,.2,1.),
         'right':   (.8,0,.2,1.),
         'forward': (.2,.2,.6,.6),
         'up':      (0,0,1.,.2),
         'down':    (0,.8,1.,.2)
         }
        transitions=\
        {'left':    standard.scrollLeft,
         'right':   standard.scrollRight,
         'forward': standard.transition,
         'up':      standard.scrollUp,
         'down':    standard.scrollDown
         }
        for ref in self._refs.keys():
            if pyzzle.design or self._refs[ref] in Slide:
                link=Slide[self._refs[ref]] if self._refs[ref] in Slide else None
                hotspot=Hotspot(self, link, id=ref, 
                                rectRel=RelativeRect(rectRels[ref]), 
                                cursor=ref+'.png', onTransition=transitions[ref],
                                layer=-1., _template=True)
                setattr(self, ref, hotspot)
                self.add(hotspot)
        if self.forward:
            self.forward.cursor='fwd.png'
            self.forward.soundfile = self._movementSoundfile
        if self.left and self.right and self.left.link == self.right.link:
            self.right.cursor='right180.png'
            self.left.cursor='left180.png'
    def _save(self):
        cells=  \
        {'id':self.id,
         'stage':self.stage.id if self.stage else None,
         'image':self.file,
         'ambientSound' :self._ambiencefile,
         'movementSound':self._movementSoundfile,
         'layer'    :self._layer,
         'dialog'   :self.dialog}
        if self.rectRel:
            for attr in 'left','top','width','height':
                cells['rect'+attr]=getattr(self.rectRel, attr)
        for ref in 'forward', 'up', 'down', 'right', 'left':
            hotspot=getattr(self,ref)
            if hotspot and hotspot.link:
                cells[ref]=hotspot.link.id
        return cells
    
    
    
    
    
    def __init__(self, id, file, stage=None, parent=None,
                 ambiencefile=None, rectRel=None, layer=0, 
                 cursor='', dialog=None):
        """Creates a slide. 
        @param id: A unique identifier for the Slide. Used to refer to the Slide 
            in scripts and the database
        @param file: The name of the image file drawn by the slide. 
        @type stage: Stage
        @param stage: An area of the game in which the slide occurs. Used to determine
            folder paths and default ambience/movement sounds.
        @type parent: Panel
        @param parent: The panel that the slide is nested within. 
            The default is pyzzle.panel.
            Note: This will not add the slide to the panel. You still need to add it
            using Slide.enter() or one of the transition functions
        @param ambiencefile: The name of the sound file that is played in a loop when
            the player reaches the slide.
        @type rectRel: RelativeRect
        @param rectRel: The rectangle occupied by the Slide.
            Currently, rect width and height do not resize the slide image.
        @type layer: float
        @param layer: The layer of the Slide. Larger numbers represent upper layers. 
            When the player clicks on an area of the Slide where two Sprites overlap,
            the sprite with the topmost layer is the only one that's activated.
        @param cursor: The name of the cursor file that is displayed when no hotspots are
            highlighted. The default is defined by Panel.cursorDefault. None displays no cursor.
        @param dialog: The name of the sound file that is played when the player reaches
            the slide for the first time. This was added specifically for the "Dryzzle" 
            video game, and may be dropped in a future version.
        """
        if id: Slide[id]=self
        if not parent: parent=pyzzle.panel
        Panel.__init__(self)
        self.id = id
        self.stage=stage
        self._file = file
        self._ambiencefile=ambiencefile
        self._movementSoundfile=None
        self._layer=layer
        self.rectRel=rectRel
        self.cursor=Panel.cursorDefault if cursor =='' else cursor
        self.dialog=dialog
        
        self.parent=parent
        self._rect=None
        self.loaded=False
        """Whether the player has loaded the slide's image file 
        in the current game session."""
        self.links=Group()
        """All Hotspots that link to this slide when clicked."""
        self.visited=False
        """Whether the player has previously visited the slide."""
        
        for ref in 'forward', 'up', 'down', 'right', 'left':
            setattr(self, ref, None)
        
    
    def _loadImage(self, image):
        self.loaded=True
        screen=pyzzle.screen.get_rect()
        rect=image.get_rect()
        rect.center=self.parent.rect.center
        if self.rectRel:
            rectAbs=self.rectRel.absolute(self.parent.rect)
            for attr in 'left','top','width','height':
                value=getattr(rectAbs, attr)
                if value:   setattr(rect,attr,value)
            
        if rect.width > screen.width:
            panHotspot=Hotspot(self, None, cursor='left.png',
                             onHighlight=standard.panLeft, 
                             onTransition=lambda *p,**k:None, 
                             layer=.1, _template=True)
            panWidth=.2
            panHotspot.rect=Rect(0, rect.top,
                                 screen.width*panWidth,
                                 rect.height)
            self.add(panHotspot)
            panHotspot=Hotspot(self, None, cursor='right.png',
                             onHighlight=standard.panRight, 
                             onTransition=lambda *p,**k:None, 
                             layer=.1, _template=True)
            panHotspot.rect=Rect(screen.width*(1-panWidth),
                                 rect.top,
                                 screen.width*(panWidth),
                                 rect.height)
            self.add(panHotspot)
        self._rect=rect
    def _getImage(self):
        """The image displayed by the Slide."""
        file=self.file
        if self.stage:
            file=os.path.join(self.stage.folder, file)
        image=media.images.load(file)
        if not self.loaded: self._loadImage(image)
        return image
    image=property(_getImage)
    
    def _getRect(self):
        """The portion of the screen occupied by the slide.
        rect coordinates are determined by rectRel. 
        If a coordinate in rectRel is None, the coordinate is 
        determined by the slide's image size. 
        """
        self._getImage()
        return self._rect
    rect=property(_getRect)

    
    def _setFile(self, file):
        self._file=file
        self.loaded=False
    def _getFile(self):
        """The name of the image file displayed by the Slide.
        Resets self.loaded to False"""
        return self._file
    file=property(_getFile, _setFile)

        
    def _getAmbiencefile(self):
        """The name of the sound file that is played in a loop when
        the player reaches the slide. If none is specified, it returns 
        the default for the slide's stage."""
        if self._ambiencefile:
            return self._ambiencefile
        if self.stage:
            return self.stage.ambientSound
    def _setAmbiencefile(self,value):
        self._ambiencefile=value
    ambiencefile=property(_getAmbiencefile, _setAmbiencefile)
    
    def draw(self, screen):
        """Draws the slide's image to screen, 
        then draws any sprites within the Slide."""
        screen.blit(self.image, self._rect)
        Panel.draw(self, screen)
        
        if pyzzle.design:
            Text.Text(self.id).draw(screen)
    def enter(self, oldslide=None, delay=.1):
        """Called when the user enters the Slide.
        @type oldslide: Panel
        @param oldslide: The Panel that was previously presented to the user,
            to be replaced by self
        @param delay: The time it should take for oldslide to transition to self
        """
        Panel.enter(self, oldslide, delay)
        if self.dialog and not self.visited:
            self.visited=True
            media.voices.load(self.dialog).play()
        if self.ambiencefile:
            ambience=media.sounds.load(self.ambiencefile)
            if ambience.get_num_channels() == 0:
                ambience.play(-1, fade_ms=int(delay*1000))
    def exit(self, newslide=None, delay=.1):
        """Called when the user exits the Slide.
        @type newslide: Panel
        @param newslide: The Panel that was previously presented to the user,
            to be replaced by self
        @param delay: The time it should take for oldslide to transition to self,
            in seconds
        """
        Panel.exit(self, newslide, delay)
        if self.ambiencefile and \
           ((not hasattr(newslide, 'ambiencefile')) or self.ambiencefile!=newslide.ambiencefile):
            ambience=media.sounds.load(self.ambiencefile)
            ambience.fadeout(int(delay*1000))

