import os
import pygame
import pyzzle
import urlparse, urllib2

class Library:
    """An object that stores data from files.  
    The object uses a function, load, to load files within a given folder. 
    If the file is not found, returns a given default file.
    If the file has already been loaded, it returns the already loaded data."""
    def __init__(self, folder, load, default=None, download=None):
        self.folder=folder
        self.default=default
        self.download=download
        self._load=load
        self.loaded={}
    def load(self, file, **param):
        if file in self.loaded:
            return self.loaded[file]
        else:
            path=os.path.join(self.folder, file)
            if os.path.exists(path):
                data=self._load(path, **param)
                self.loaded[file]=data
            elif file==self.default:
                raise 'Could not load default file: '+str(self.default)
            elif not self.default:
                raise 'Could not load file: '+str(file)
            elif self.download:
                base=self.download
                base2 = urlparse.urljoin(base, self.folder)+'/'
                url = urlparse.urljoin(base2, file)
                url = url.replace(' ', '%20')
                url = url.replace('\\', '/')
                request = urllib2.Request(url)
                try:
                    print('downloading from '+url)
                    downloader = urllib2.urlopen(request)
                    download = open(path, "wb")
                    download.write(downloader.read())
                    download.close()
                    data=self._load(path, **param)
                    self.loaded[file]=data
                except urllib2.HTTPError, ex:
                    print(str(ex.code)+' Could not find file: '+str(url))
                    data=self.load(self.default)
            else:
                print('Could not load file: '+str(file))
                data=self.load(self.default)
            return data
    def unload(self, file):
        if file in self.loaded:
            del self.loaded[file]
            
def loadImage(path):            return pygame.image.load(path).convert_alpha()
def loadFont(path, fontSize=16):return pygame.font.Font(path, fontSize)
def loadSound(path):            return pygame.mixer.Sound(path)
def loadMovie(path):            return pygame.movie.Movie(path)
images=Library('pictures',  loadImage, default='default.gif')
movies=Library('Movies',  loadMovie)
cursors=Library('cursors',  loadImage, default='arrow.png')
fonts =Library('fonts',     loadFont)
sounds=Library('sounds/effects',    loadSound, default='../default.wav')
voices=Library('sounds/voices',    loadSound, default='../default.wav')
