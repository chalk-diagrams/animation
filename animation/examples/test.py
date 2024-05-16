from animation.core import Animation
from chalk import *

dia = circle(1)
frame = rectangle(6, 2)

anim = Animation(0, 1, lambda t: dia.translate(t * 2, 0) + frame)
anim.render_gif("output/test.gif", 24)
