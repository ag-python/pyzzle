import pyzzle

pyzzle.design=True
pyzzle.init(name='Dryzzle')
pyzzle.load('main.game')

pyzzle.transition(newslide=pyzzle.Slide['start'])
pyzzle.play()