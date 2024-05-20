from colour import Color
from chalk import Trail, V2, rectangle, concat, with_envelope, empty, Diagram
from functools import reduce

from animation.core import constant, animation, render_gif, Animation
from animation.active import (
    after,
    map_with_time,
    movie_add,
    sequence_add,
    shift,
    splice,
    stretch,
    trim_after,
    trim_before,
)

a = 1.25
b = 2.00


def make_triangle():
    t = Trail.from_offsets([V2(a, 0), V2(0, -b)], closed=True)
    t = t.stroke()
    t = t.fill_color(Color("yellow"))
    return t.translate(-(a + b) / 2, -(a - b) / 2)


ts = [make_triangle().rotate(90 * i) for i in range(4)]

sq = rectangle(b - a, b - a)
sq = sq.fill_color(Color("yellow"))

frame = rectangle(5, 5)
frame = frame.fill_color(Color("gray"))


def appear(d: Diagram) -> Animation:
    def func(t):
        if t <= 0.0:
            return empty()
        else:
            return d

    return animation(func)


def make_appear():
    anims = [appear(t) for t in ts]
    return constant(sq) + movie_add(anims)


def move_triangles():
    background = constant(sq) + constant(ts[1]) + constant(ts[2])
    # Not a great API...
    return background + splice(
        animation(lambda t: ts[0].translate(t * b, t * a) + ts[3]),
        animation(lambda t: ts[0].translate(b, a) + ts[3].translate(-t * a, t * b)),
    )


anim = constant(frame) + splice(make_appear(), move_triangles())
render_gif(anim, "examples/output/pythagoras.gif", 24)
