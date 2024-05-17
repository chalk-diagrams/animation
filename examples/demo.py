from animation.core import constant, animation, render_gif
from colour import Color
from chalk import circle, rectangle

papaya = Color("#ff9700")
blue = Color("#005FDB")

obj = circle(1).fill_color(blue)
frame = rectangle(6, 3).fill_color(papaya)

anim = constant(frame) + animation(lambda t: obj.translate(2 * t - 1, 0))
render_gif(anim, "examples/output/demo.gif", 24)
