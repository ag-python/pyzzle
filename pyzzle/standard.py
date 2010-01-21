"""
    A collection of commonly used, global functions
"""
import Text
import Movie
import pyzzle
import media
import pygame
import sys
import math
from pygame.locals import *

def beginDraw():
    """Runs the draw() method on pyzzle.panel.
    Useful for creating custom transitions."""
    pyzzle.screen.fill((0,0,0))
    pyzzle.panel.draw(pyzzle.screen)
def endDraw():
    """Finalizes drawing. 
    Useful for creating custom transitions."""
    pygame.display.flip()
def drawCursor(cursor, pos=None):
    """Displays the cursor
    Useful for creating custom transitions."""
    if cursor:
        if not pos: pos=pygame.mouse.get_pos()
        pyzzle.cursor.image=media.cursors.load(cursor)
        pyzzle.cursor.rect=pyzzle.cursor.image.get_rect()
        pyzzle.cursor.rect.center=pos
        pyzzle.screen.blit(pyzzle.cursor.image, pyzzle.cursor.rect)
def draw():
    """Draws everything in pyzzle.panel. Does not run any highlight() methods."""
    beginDraw()
    endDraw()

def pause(delay=1):
    """Pauses the game.
    @param delay: The number of seconds to pause the game.
    """
    framecount=int(delay*pyzzle.framerate)
    for i in range(framecount):
        draw()

def dragRect(color=(0,0,0)):
    """Waits for user to drag the mouse.
    Draws a rectangle that highlights the user's selection.
    @type color: (int,int,int)
    @param color: Color of the rectangle to be drawn.
    @rtype: Rect
    @return: The user's selection.
    """
    left,top=pygame.mouse.get_pos()
    selected=Rect(left,top,0,0)
    mouseDown=True
    while mouseDown:
        pyzzle.beginDraw()
        
        right,bottom=pygame.mouse.get_pos()
        selected=Rect(min(left,right),
                      min(top,bottom),
                      abs(right-left),
                      abs(bottom-top))
        pygame.draw.rect(pyzzle.screen, color, selected, 2)
        pyzzle.endDraw()
        
        for event in pygame.event.get():
            if event.type==MOUSEBUTTONUP:
                mouseDown=False
    return selected


def dragLines(pointlist, cursor='fist.png'):
    """Waits for user to drag the mouse. 
    @param cursor: Name of the cursor file to display while dragging 
    @param pointlist: 
    @rtype: (int,int)
    @return: coordinates of the cursor after the drag."""
    mouseDown=True
    #pygame.mouse.set_pos(pointlist[0])
    x,y=pygame.mouse.get_pos()
    closest=None
    while mouseDown:
        pyzzle.beginDraw()
        
        x,y = pygame.mouse.get_pos()
        closest=x,y
        closestDistance=1e10
        x1,y1 = pointlist[0]
        for x2,y2 in pointlist[1:]:
            
            dx,dy = x2-x1, y2-y1
            if   dx==0: xx,yy=x1,y
            elif dy==0: xx,yy=x,y1
            else:
                #find equation for line, y=mx+b
                m = float(dy)/float(dx)
                b = y1 - (m * x1)
                #find equation for perpendicular line, y=nx+c
                n = -1./m
                c = y  - (n * x)
                #find intersection of the two lines, or x where mx+b=nx+c
                xx = (b - c) / (n - m)
                yy = m * xx + b
                #x and y must not exceed line segment 
                if    xx > x1 > x2 or xx < x1 < x2: 
                    xx=x1
                    yy=y1
                elif  xx > x2 > x1 or xx < x2 < x1: 
                    xx=x2
                    yy=y2
                
            distance=math.sqrt((xx-x)**2 + (yy-y)**2) 
            if distance < closestDistance:
                closestDistance=distance
                closest=xx,yy
            x1,y1 = x2,y2
            
        pyzzle.drawCursor(cursor, pos=closest)
        pyzzle.endDraw()
        for event in pygame.event.get():
            if event.type==MOUSEBUTTONUP:
                mouseDown=False
                
    return closest==pointlist[-1]
    
def drag(cursor='fist.png'):
    """Waits for user to drag the mouse. 
    @param cursor: Name of the cursor file to display while dragging 
    @rtype: (int,int)
    @return: coordinates of the cursor after the drag."""
    mouseDown=True
    while mouseDown:
        pyzzle.beginDraw()
        x,y=pygame.mouse.get_pos()
        pyzzle.drawCursor(cursor)
        pyzzle.endDraw()
        
        for event in pygame.event.get():
            if event.type==MOUSEBUTTONUP:
                mouseDown=False
    return x,y

def prompt(text, color=None, fontSize=36):
    """Prompts a message to the user. 
    The user may press any key so any mousebutton to continue.
    @param text: The message to display.
    @param color: The color of message text.
    @param fontSize: The size of message text.
    """
    textSprite=Text.Text(text, fontSize=fontSize, color=color)
    textSprite._getImage()
    screenrect=pyzzle.screen.get_rect()
    textSprite.rect.center=screenrect.center
    done=False
    while not done:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            done=event.type == KEYDOWN or event.type == MOUSEBUTTONDOWN
        beginDraw()
        textSprite.draw(pyzzle.screen)
        endDraw()
def promptText(question='', answer='', numeric=False, allowExit=True, color=None, fontSize=36):
    """Prompts the user to input text. 
    @param question: A question to display to the user.
    @param answer: The default answer.
    @param numeric: Whether only numeric characters are allowed.
    @param allowExit: Whether the user may escape the prompt by hitting ESC
    @param color: The color of question and answer text.
    @param fontSize: The size of question and answer text.
    @rtype: string
    @return: The text the user has entered, or None if the user escaped the prompt.
    """
    questionSprite=Text.Text(question, fontSize=fontSize, color=color)
    answerSprite=Text.Text(answer, fontSize=fontSize, color=color)
    questionSprite._getImage()
    answerSprite._getImage()
    screenrect=pyzzle.screen.get_rect()
    questionSprite.rect.center=screenrect.center
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE and allowExit:
                    return None
                elif event.key == K_BACKSPACE:
                    answer=answer[:-1]
                elif event.key in (K_RETURN, K_KP_ENTER):
                    if len(answer)>0:
                        return answer
                    elif allowExit:
                        return None
                else:
                    key=pygame.key.name(event.key)
                    key=' ' if key=='space' else key
                    key='' if len(key)>1 else key
                    key='' if key not in '0123456789.' and numeric else key
                    if pygame.key.get_mods() & KMOD_SHIFT:
                        key=key.upper()
                        upper={'-':'_'}
                        key=upper[key] if key in upper else key
                    answer+=key
        answerSprite.rect.midtop=questionSprite.rect.midbottom
        answerSprite.setText(answer)
        beginDraw()
        questionSprite.draw(pyzzle.screen)
        answerSprite.draw(pyzzle.screen)
        endDraw()
def promptNumber(question='', **param):
    """Prompts the user to input a number. 
    @see: promptText
    @param question: A question to display to the user.
    @param **param: Arguments of the promptText function.
    @rtype: float
    @return: The number the user has entered, or None if the user escaped the prompt.
    Returns a float or None if user escapes from prompt.
    """
    answer=promptText(question, numeric=True, **param)
    try: answer=float(answer)
    except: answer=None
    return answer
def promptChoice(question='', choices=[], allowExit=True, color=None, fontFile=None, fontSize=None, spacing=20, selectionColor=None):
    """Prompts the user to answer a multiple choice question.
    @param question: A question to display to the user.
    @param choices: The choices the user may select.
    @param allowExit: Whether the user may escape the prompt by hitting ESC
    @param color: The color of question and choice text.
    @param fontSize: The size of question and answer text.
    @param spacing: The spacing between each choice, in pixels.
    @param param: The color of choice text when highlighted by the user.
    @rtype: string
    @return: The text the user has selected, or None if the user escaped the prompt.
    """
    if not color: color=Text.Text.colorDefault
    if not selectionColor: selectionColor=color
    screenrect=pyzzle.screen.get_rect()
    questionSprite=Text.Text(question, fontFile=fontFile, fontSize=fontSize, color=color)
    questionSprite._getImage()
    questionSprite.rect.center=screenrect.center
    prevSprite=questionSprite
    choiceSprites=pygame.sprite.Group()
    for choice in choices:
        choiceSprite=Text.Text(choice, fontFile=fontFile, fontSize=fontSize, color=color)
        choiceSprite._getImage()
        choiceSprite.rect.center=screenrect.center
        choiceSprite.rect.top=prevSprite.rect.bottom+spacing
        choiceSprites.add(choiceSprite)
        prevSprite=choiceSprite
    while True:
        selection=None
        beginDraw()
        questionSprite.draw(pyzzle.screen)
        for choiceSprite in choiceSprites:
            choiceSprite.color=color
            if choiceSprite.rect.collidepoint(pyzzle.cursor.rect.center):
                choiceSprite.color=selectionColor
                selection=choiceSprite
            choiceSprite.draw(pyzzle.screen)
        pyzzle.cursor.rect.topleft=pygame.mouse.get_pos()
        drawCursor('fwd.png' if selection else 'default.png')
        endDraw()

        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE and allowExit:
                    return None
            if event.type == MOUSEBUTTONDOWN:
                if selection: return selection.text
        
#highlight functions
def _pan(self, towards, aways):
    screen=pyzzle.screen.get_rect()
    mousex, mousey=pyzzle.cursor.rect.center
    distance=getattr(self.rect,aways)-mousex
    distance*=.1
    if not (screen.left <= getattr(self.parent.rect, towards)+distance <= screen.right):
        self.parent.rect.move_ip(distance,0)
    else: 
        setattr(self.parent.rect, aways, getattr(screen, aways))
def panRight(self):
    """Moves the slide right, and jumps back to the slide's left when it con go no further. 
    Used in panoramic slides."""
    _pan(self, towards='right', aways='left')
def panLeft(self): 
    """Moves the slide left, and jumps back to the slide's right when it con go no further. 
    Intended as a choice for Hotspot.onHighlight. Used in panoramic slides."""
    _pan(self, towards='left', aways='right')

#transition functions
def beginTransition(oldslide, newslide, delay=0, panel=None):
    """Prepares slides for transition. 
    @attention: Must be used when creating custom transition functions.
    @type oldslide: Panel
    @param oldslide: The Panel to exit.
    @type newslide: Panel
    @param newslide: The Panel to enter.
    @param delay: The time it should take to perform onStart and onStop 
        individually, in seconds.
    @type panel: Panel
    @param panel: The new parent panel of newslide. pyzzle.panel by default. 
    """
    if not panel:
        if hasattr(oldslide, 'parent'): panel=oldslide.parent
        else:                           panel=pyzzle.panel
    if newslide:
        newslide.parent=panel
        newslide._getRect()
        panel.add(newslide)
    if hasattr(oldslide, 'exit'):
        oldslide.exit(newslide, delay)
    if hasattr(newslide, 'enter'):
        newslide.enter(oldslide, delay)
def endTransition(oldslide, newslide, delay=0, panel=None):
    """Finalizes slide transition. 
    @attention: Must be used when creating custom transition functions.
    @type oldslide: Panel
    @param oldslide: The Panel to exit.
    @type newslide: Panel
    @param newslide: The Panel to enter.
    @param delay: The time it should take to perform onStart and onStop 
        individually, in seconds.
    @type panel: Panel
    @param panel: The new parent panel of newslide. pyzzle.panel by default. 
    """
    if not panel:
        if hasattr(oldslide, 'parent'): panel=oldslide.parent
        else:                           panel=pyzzle.panel
    if oldslide:
        panel.remove(oldslide)
    pyzzle.history.append((oldslide, newslide))
def _noTransition(*p,**k):
    pass
def transition(oldslide=None, newslide=None, delay=0, **param):
    """Basic transition function.
    Pauses the game for a given number of seconds, then flashes to newslide
    @type oldslide: Panel
    @param oldslide: The Panel to exit.
    @type newslide: Panel
    @param newslide: The Panel to enter.
    @param delay: The time it should take to perform onStart and onStop 
        individually, in seconds.
    @param **param: Additional arguments used in beginTransition() and endTransition()
    """
    beginTransition(oldslide, newslide, delay, **param)
    pause(delay)
    endTransition(oldslide, newslide, delay, **param)
def _scroll(oldslide, newslide, towards, aways, delay=0, **param):
    beginTransition(oldslide, newslide, delay, **param)
    screen=pyzzle.screen.get_rect()
    
    oldsliderect = oldslide.rect if oldslide else Rect(screen)
    newsliderect = newslide.rect if newslide else Rect(screen)
    setattr(newsliderect, aways, getattr(oldsliderect, towards))
    screenx, screeny=screen.center
    slidex, slidey=newsliderect.center
    distancex, distancey=screenx-slidex, screeny-slidey
    framecount=int(delay*pyzzle.framerate)
    increment=(distancex/framecount, distancey/framecount) if framecount else (0,0)
    
    for i in xrange(0, framecount):
        if oldslide:    oldslide.rect.move_ip(*increment)
        if newslide:    newslide.rect.move_ip(*increment)
        draw()
    if oldslide:    oldslide.rect.center=pyzzle.screen.get_rect().center
    if newslide:    newslide.rect.center=pyzzle.screen.get_rect().center
    endTransition(oldslide, newslide, delay, **param)
def _scrollfn(towards, aways):
    def scroll(oldslide=None, newslide=None, delay=0, **param):
        _scroll(oldslide, newslide, towards, aways, delay, **param)
    return scroll
scrollRight =_scrollfn('right', 'left')
scrollLeft  =_scrollfn('left', 'right')
scrollDown  =_scrollfn('bottom', 'top')
scrollUp    =_scrollfn('top', 'bottom')
    
def fade(oldslide=None, newslide=None, delay=0, color=(0,0,0), alpha=255, **param):
    """Transitions slides by fade in/out. Currently works best on full screen slides.
    @type oldslide: Panel
    @param oldslide: The Panel to fade out of.
    @type newslide: Panel
    @param newslide: The Panel to fade in to.
    @param delay: The time it should take perform each fade in/fade out.
    @type color: (int,int,int)
    @param color: The color at maximum fade
    @param alpha: The alpha transparency of the slide at maximum fade
    @param **param: Additional arguments used in beginTransition() and endTransition()
    """
    if not (oldslide and newslide):
        delay=delay*2
    framecount=int(delay*pyzzle.framerate)
    increment=1./(framecount) if framecount else 1.
    filter=pyzzle.screen.copy()
    filter.fill(color)
    filter.set_alpha(alpha)
    if oldslide:
        for i in range(framecount):
            beginDraw()
            filter.set_alpha(int(alpha*increment*i))
            pyzzle.screen.blit(filter, (0,0))
            endDraw()
    beginTransition(oldslide, newslide, delay, **param)
    endTransition(oldslide, newslide, delay, **param)
    if newslide:
        for i in range(framecount):
            beginDraw()
            filter.set_alpha(int(alpha*(1-(increment*i))))
            pyzzle.screen.blit(filter, (0,0))
            endDraw()


def cutscene(oldslide=None, newslide=None, delay=0, 
             onStart=fade, onStop=fade, allowExit=True,
             moviefile=None, soundfile=None, movie=None, **param):
    """Transitions from oldslide, plays a movie, and transitions back to newslide.
    @type oldslide: Panel
    @param oldslide: The Panel to exit.
    @type newslide: Panel
    @param newslide: The Panel to enter.
    @param delay: The time it should take to perform onStart and onStop 
        individually, in seconds.
    @param onStart: The transition function used to transition from oldslide to the movie
    @param onStop: The transition function used to transition from the movie to newslide 
    @param allowExit: Whether the user can skip the movie by hitting ESC.
    @param moviefile: The name of the movie file to play. 
        Pygame currently only supports the MPEG-1 video codec. 
    @param soundfile: The name of the sound file to play along with the movie.
        Any sound from the movie will be replaced with this sound.
        Use this if you are having trouble getting movie sound to play in Pygame.
    @type movie: Movie
    @param movie: An instance of the Movie class to play. If specified, 
        any file you specify with the moviefile parameter will be ignored.
    @param **param: Additional arguments used in beginTransition() and endTransition()
    """
    if not movie:
        movie=Movie.Movie(id=None, moviefile=moviefile, soundfile=soundfile)
    stopped=False
    onStart(oldslide, movie, delay)
    clock = pygame.time.Clock()
    while not (movie.played or stopped):
        clock.tick(150)
        pyzzle.framerate=clock.get_fps()
        draw()
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE and allowExit:
                    stopped=True
    onStop(movie, newslide, delay)