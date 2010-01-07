import pygame, sys, sqlite3

import pyzzle
import DB
from Slide import Slide
from Hotspot import Hotspot
from Switch import Switch
from Item import Item
from Panel import Panel
from Text import Text
from standard import *
import os

panel=Panel()
cursor=pygame.sprite.Sprite()
cursor.rect=Rect(0,0,0,0)
cursor.image=pygame.Surface((0,0))
screen=None
framerate=30
datafile=None
globals=DB.Table('globals', (object,), {})
stages=DB.Table('stages', (object,), {})
design=False
menu=sys.exit
history=[]

def init(screensize=(800,600), name='Pyzzle', iconfile=None):
    """Initializes the screen. Must call before anything else.
    @type screensize: (int,int)
    @param screensize: Dimensions of the screen.
    @type name: string
    @param name: Text to display in the window's title bar
    @param iconfile: name of the image file to display as the window's icon
    """
    pygame.init()
    pyzzle.screen=pygame.display.set_mode(screensize)
    pyzzle.panel.rect=pyzzle.screen.get_rect()
    if iconfile:
        icon=pygame.image.load(iconfile).convert_alpha()
        pygame.display.set_icon(icon)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption(name)
def load(datafilename):
    """Loads game data from a SQLite database file.
    @param datafilename: name of the SQLite database file to load
    """
    pyzzle.datafile=DB.DB(datafilename)
    
    stages.rows.update(**datafile.select('Stage',value=lambda row: row,key=lambda row: row.id))
    datafile.select('Slide', value=lambda row:Slide._load(row))
    for slide in Slide:  slide._loadRefs()
    datafile.select('Hotspot', value=lambda row:Hotspot._load(row))
    datafile.select('Item',value=lambda row:Item._load(row))
    datafile.select('Switch',value=lambda row:Switch._load(row))

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
            datafile.query('update Slide set image = ? where lower(image)=lower(?)', 
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
                pyzzle.datafile.close()
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
            if event.type == MOUSEBUTTONDOWN:
                pyzzle.panel.click(design=(pygame.mouse.get_pressed()[2] and pyzzle.design))
                