import pyzzle

pyzzle.Text.Text.colorDefault=(255,0,255)
pyzzle.design=True
pyzzle.init(screensize=(640,480))
pyzzle.load('main.game')

pyzzle.transition(newslide=pyzzle.Slide['room-4-1'])
pyzzle.play()