"""Presents video/audio to the user in a manner similar to Slides"""
import pygame, os, pyzzle
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.sprite import Group
from Panel import Panel
import media

class Movie(Panel):
    """Presents video/audio to the user in a manner similar to Slides.
    
    Like the Slide, movies can blit an image to the screen, 
    perform click and highlight behavior, nest within Panels, 
    and even nest Sprites such as Hotspots, Text, and Slides. 
    
    It is worth mentioning that Pygame has limited support for
    movies, and these limitations transfer to Pyzzle. 
    Movie files must use the MPEG-1 video codec. If the movie files
    contain audio, they must use the MPEG-2 audio codec (not MP2), 
    and no other sounds can play alongside them. As of 0.9,
    I have not been able to get sound to play from movie files.
    However, you can specify a seperate audio file to play alongside
    the movie using the soundfile attribute. This has the added
    benefit of being able to play alongside other sounds.
    """
    def __init__(self, id, moviefile, soundfile=None, stage=None, 
                 rectRel=None, layer=0, loop=False, onStop=lambda:None):
        """Creates a Movie
        @param id: A unique identifier for the Movie. 
        @param moviefile: The name of the movie file to be played
        @param soundfile: The name of the sound file to be played in sync 
            with the movie. Use this parameter if you cannot get sound
            to work from your movie file, or if you would like other sounds
            to play along with the movie (ambience, music, effects, etc.)
        @type stage: Stage
        @param stage: An area of the game in which the movie occurs. Used to determine
            folder paths.
        @type rectRel: RelativeRect
        @param rectRel: The rectangle occupied by the Movie. 
            rect width and height do not resize the movie - this is a limitation
            within Pygame.
        @type layer: float
        @param layer: The layer of the Movie. Larger numbers represent upper layers. 
            Upper layers will draw over lower layers.
        @type boolean: 
        @param loop: Whether the movie should loop endlessly.
        @param onStop: The function that plays upon completion of the movie.
            If loop=True, this function will never fire.
        """
        Panel.__init__(self)
        self.id = id
        self.file = moviefile
        self.stage=stage
        self.rectRel=rectRel
        self._rect=None
        self._layer=layer
        self.loaded=False
        self.surface=None
        self.onStop=onStop
        self.loop=loop
        self.played=False
        
        self.soundfile=soundfile
        if stage:
            self.file=os.path.join(stage.folder, self.file)
    
    def _load(self):
        movie=media.movies.load(self.file)
        self.loaded=True
        screen=pyzzle.screen.get_rect()
        rect=Rect((0,0),movie.get_size())
        rect.center=screen.center
        if self.rectRel:
            left,top,width,height=self.rectRel
            if width:   rect.width =width *screen.width
            if height:  rect.height=height*screen.height
            rect.center=screen.center
            if left:    rect.left=left*screen.width
            if top:     rect.top=top*screen.height
        self._rect=rect
        self.surface=pygame.surface.Surface((rect.width, rect.height))
        movie.set_display(self.surface)
    def _getMovie(self):
        """The movie that is played."""
        if not self.loaded: self._load()
        return media.movies.load(self.file)
    movie=property(_getMovie)
    def _getRect(self):
        """The coordinates of the movie.
        rect coordinates are determined by rectRel. 
        If a coordinate in rectRel is None, the coordinate is 
        determined by the slide's image size. 
        """
        self._getMovie()
        return self._rect
    rect=property(_getRect)

    
    def draw(self, screen):
        """Renders the movie to the screen, 
        then draws any sprites within the Movie."""
        movie=self._getMovie()
        if not movie.get_busy():
            if self.loop:
                movie.rewind()
            elif not self.played:
                self.played=True
                self.exit(delay=0)
                self.onStop()
        screen.blit(self.surface, self._rect)
        Panel.draw(self, screen)
    def enter(self, oldslide=None, delay=.1):
        """Called when the user encounters the Movie.
        @type oldslide: Panel
        @param oldslide: The Panel that was previously presented to the user,
            to be replaced by self
        @param delay: The time it should take for oldslide to transition to self
        """
        movie=self._getMovie()
        if self.soundfile:
            sound=media.sounds.load(self.soundfile)
            sound.play(-1, fade_ms=int(delay*1000))
        elif movie.has_audio():
            pygame.mixer.quit()
            movie.set_volume(1.0)
        movie.play()
    def exit(self, newslide=None, delay=.1):
        """Called when the user exits the Movie.
        @type newslide: Panel
        @param newslide: The Panel that was previously presented to the user,
            to be replaced by self
        @param delay: The time it should take for oldslide to transition to self,
            in seconds
        """
        movie=self._getMovie()
        if self.soundfile:
            sound=media.sounds.load(self.soundfile)
            sound.fadeout(int(delay*1000))
        movie.stop()