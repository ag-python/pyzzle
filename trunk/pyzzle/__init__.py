import pygame, sys, sqlite3

import pyzzle
import gamefile
from slide import Slide
from hotspot import Hotspot
from switch import Switch
from item import Item
from panel import Panel
from text import Text
from standard import *
import os

panel=Panel()
cursor=pygame.sprite.Sprite()
cursor.rect=Rect(0,0,0,0)
cursor.image=pygame.Surface((0,0))
screen=None
framerate=30
gamefile=None
globals=datafile.Table('globals', (object,), {})
stages=datafile.Table('stages', (object,), {})
design=False
zip=True
menu=sys.exit
history=[]

def init(screensize=(800,600), name='Pyzzle', iconfile=None, fullscreen=False):
    """Initializes the screen. Must call before anything else.
    @type screensize: (int,int)
    @param screensize: Dimensions of the screen.
    @type name: string
    @param name: Text to display in the window's title bar
    @param iconfile: name of the image file to display as the window's icon
    """
    pygame.init()
    pyzzle.screen=pygame.display.set_mode(screensize, 
                                          pygame.FULLSCREEN if fullscreen else 0)
    pyzzle.panel.rect=pyzzle.screen.get_rect()
    if iconfile:
        icon=pygame.image.load(iconfile).convert_alpha()
        pygame.display.set_icon(icon)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(name)
def load(gamefilename):
    """Loads game data from an SQLite database file.
    @param datafilename: name of the SQLite database file to load
    """
    pyzzle.gamefile=datafile.DB(gamefilename)
    
    stages.rows=gamefile.load(datafile.Row,'Stage')
    gamefile.load(Slide)
    for slide in Slide:  slide._loadRefs()
    gamefile.load(Hotspot)
    gamefile.load(Item)
    gamefile.load(Switch)
    
def save(gamefilename=None):
    """Saves game data to an SQLite database file.
    @param datafilename: name of the SQLite database file to load,
        or the currently loaded file, if none specified
    """
    if gamefilename:
        pyzzle.gamefile=datafile.DB(gamefilename)
    gamefile.save(Slide)
    gamefile.save(Hotspot)
    
def cleanup():
    """Corrects capitalization of any image files mentioned in 
    the loaded SQLite database file. 
    Useful to prepare for distribution using dynamically downloaded content,
    but takes a while to run."""
    for stage in stages:
        directory=os.path.join('pictures',stage.folder)
        print directory
        for file in os.listdir(directory):
            print file
            gamefile.query('update Slide set image = ? where lower(image)=lower(?)', 
                           (file,file))
def play():
    """The main game loop. Call this function only after you have finished 
    scripting and other initialization."""
    clock = pygame.time.Clock()
    while True:
        #update/draw the game
        clock.tick(150)
        pyzzle.framerate=clock.get_fps()
        
        pyzzle.beginDraw()
        pyzzle.drawCursor(pyzzle.panel.highlight())
        pyzzle.endDraw()
        
        #process user input - MUST COME AFTER DRAW
        #(cursor pos needs to be set when calling pyzzle.panel.click())
        for event in pygame.event.get():
            if event.type == QUIT:
                pyzzle.gamefile.close()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pyzzle.menu()
                if  pyzzle.design and pygame.key.get_mods() & KMOD_CTRL:
                    if event.key == K_z:
                        if pyzzle.history:
                            oldslide, newslide=pyzzle.history.pop(-1)
                            if oldslide:
                                pyzzle.transition(newslide, oldslide, 0)
                                pyzzle.history=pyzzle.history[0:-1]
                    elif event.key==K_g:
                        slidename = pyzzle.promptText('Enter slide to jump to:')
                        if slidename in Slide.rows:
                            pyzzle.panel.sprites.empty()
                            pyzzle.panel.add(Slide[slidename])
                    elif event.key==K_s:
                        pyzzle.save()
                        pyzzle.prompt('Game saved')
            if event.type == MOUSEBUTTONDOWN:
                pyzzle.panel.click(design=(pygame.mouse.get_pressed()[2] and pyzzle.design))
                