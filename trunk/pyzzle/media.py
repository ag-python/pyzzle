"""Provides high level functionality for accessing media from files"""
import os
import pygame
import pyzzle
import urlparse, urllib2

class Library:
    """Loads and stores data from files.
    
    A pattern often emerges when handling files for video games:
    check to see if a file exists in a group of folders organized by content type,
    load the file if it exists, display a place-holder file if something goes wrong, 
    and most importantly, store the data in the event we want to reach it again. 
    
    The Library class handles this pattern. Libraries are used throughout 
    Pyzzle to lazily initialize persistant content in a Pythonic fashion. 
    Content from files can be loaded by either the load() method 
    (e.g. images.load('foobar.jpg')) or as a dictionary (e.g. images['foobar.jpg'] ).
    
    In addition, a URL can be specified from which files will download in the
    event they are not found on the local machine. This frees you from restrictions
    imposed on the size of your distributable - a game from a 10 MB installer file 
    could access thousands of MB in content. """
    def __init__(self, folder, load, default=None, download=None):
        """Creates a Library.
        @param folder: The relative folder path from which content from this library
            may be accessed.
        @param load: The load function that runs upon requesting to load a file 
            for the first time. Accepts the name of the file and returns 
            the data contained within the file.
        @param default: The default data that will be presented in the event 
            something goes wrong when loading the file.
        @param download: The name of the URL from which to download content,
            in the event content is not on the local machine.
        """
        self.folder=folder
        self.default=default
        self.download=download
        self._load=load
        self.loaded={}
    def __getitem__(self, key):
        return self.load(key)
    def __delitem__(self, key):
        self.delete(key)
    def load(self, file, **param):
        """Loads the file from self.folder. 
        Retrieves existing data in the event the file has been previously loaded, 
        downloads content from the internet in the event of an error
        (if url is specified), and displays self.default if all else fails 
        (if default content is specified). Throws an exception if an error occurs 
        that is not resolved from a download or default content. 
        """
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
    def delete(self, file):
        """Deletes data loaded from the file, if present. 
        Implementing behavior that uses this function may be more
        trouble than its worth. Only consider this if You're game slows
        down considerably as more and more content is loaded. Even on 
        a large (1000+ slide) project, this shouldn't happen when
        using reasonable slide resolutions. 
        """
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
