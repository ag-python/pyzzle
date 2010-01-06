import pygame, os, pyzzle
from pygame.rect import Rect
from pygame.surface import Surface
from pygame.sprite import Group
from Panel import Panel
import media

class Movie(Panel):
    def __init__(self, id, moviefile, soundfile=None, stage=None, 
                 rectRel=None, layer=0, loop=False, onStop=lambda:None):
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
        if not self.loaded: self._load()
        return media.movies.load(self.file)
    movie=property(_getMovie)
    def _getRect(self):
        self._getMovie()
        return self._rect
    rect=property(_getRect)

    
    def draw(self, screen):
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
    def click(self, **param):
        for sprite in self.sprites:
            sprite._getRect()
        Panel.click(self, **param)
    def enter(self, oldslide=None, delay=.1):
        movie=self._getMovie()
        if self.soundfile:
            sound=media.sounds.load(self.soundfile)
            sound.play(-1, fade_ms=int(delay*1000))
        elif movie.has_audio():
            pygame.mixer.quit()
            movie.set_volume(1.0)
        movie.play()
    def exit(self, newslide=None, delay=.1):
        movie=self._getMovie()
        if self.soundfile:
            sound=media.sounds.load(self.soundfile)
            sound.fadeout(int(delay*1000))
        movie.stop()