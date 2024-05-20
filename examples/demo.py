from colour import Color
from chalk import circle, rectangle

from animation.core import constant, animation, render_gif
from animation.active import stretch, map_with_time

papaya = Color("#ff9700")
blue = Color("#005FDB")

obj = circle(1).fill_color(blue)
frame = rectangle(6, 3).fill_color(papaya)

anim_obj = animation(lambda _: obj)
anim_obj = map_with_time(anim_obj, lambda t, o: o.translate(2 * t - 1, 0))
# anim_obj = map_with_time(anim_obj, lambda t, o: o.scale_uniform_to_x(1 + t))
anim_obj = stretch(anim_obj, 1)

anim = constant(frame) + anim_obj
render_gif(anim, "examples/output/demo.gif", 24)
