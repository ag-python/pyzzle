import pyzzle

pyzzle.init(name='Dryzzle', fullscreen=True)
pyzzle.load('main.game')

def switchCurtains(switch):
    pyzzle.Slide['room-1-4'].file='room-1-4b.jpg' if switch.on else 'room-1-4.jpg'
    pyzzle.Slide['room-4-4'].file='room-4-4b.jpg' if switch.on else 'room-4-4.jpg'
    pyzzle.Slide['room-4-1'].file='room-4-1b.jpg' if switch.on else 'room-4-1.jpg'
    switch.switch()
pyzzle.Switch['curtains'].onSwitch=switchCurtains

pyzzle.transition(newslide=pyzzle.Slide.start)
pyzzle.play()