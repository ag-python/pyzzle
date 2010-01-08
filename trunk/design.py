import pyzzle

pyzzle.Text.Text.colorDefault=(255,0,255)
pyzzle.design=True
pyzzle.init(name='Dryzzle', fullscreen=False)
pyzzle.load('main.game')

pyzzle.transition(newslide=pyzzle.Slide['room-4-1'])
pyzzle.play()