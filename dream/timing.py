"""Single timing source for unchanged picture and synchronized sound (seconds/phases)."""
FPS = 30
DURATION = 60
CYCLE = 6
PRESS_SHAPE = (.24, .34)
CUT_SHAPE = (.27, .35)
COAT_COLOR = (.21, .46)
EVENTS = {'press': PRESS_SHAPE[0]*CYCLE, 'cut': CUT_SHAPE[0]*CYCLE,
          'coat': COAT_COLOR[0]*CYCLE}
