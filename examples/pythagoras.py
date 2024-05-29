import pdb
from colour import Color
from chalk import Trail, V2, rectangle, concat, with_envelope, empty, Diagram, text
from functools import reduce

from animation.core import constant, animation, render_gif, Animation
from animation.active import (
    after,
    map_with_time,
    movie_add,
    sequence_add,
    shift,
    movie,
    splice,
    stretch,
    trim_after,
    trim_before,
)

# Triangle sizes
a = 1.25
b = 2.00


offset_x = -(a + b) / 2
offset_y = -(a - b) / 2


def make_triangle():
    t = Trail.from_offsets([V2(a, 0), V2(0, -b)], closed=True)
    t = t.stroke()
    t = t.fill_color(Color("yellow"))
    return t.translate(offset_x, offset_y)


ts = [make_triangle().rotate(90 * i) for i in range(4)]

sq = rectangle(b - a, b - a)
sq = sq.fill_color(Color("yellow"))

frame = rectangle(5, 5)
frame = frame.fill_color(Color("gray"))


def annot(t, pos):
    return text(t, 0.3).fill_color(Color("black")).translate(*pos)


# Position of annotations
pos_tl = (-1.5, -2)
pos_tr = (+1.5, -2)

annot_tl = annot("area = c²", pos_tl)
annot_tr = annot("area = a² + b²", pos_tr)

# Final squares
make_sq = lambda x: rectangle(x, x).fill_color(Color("yellow"))
# fmt: off
sqs_final = (
    make_sq(a).align_bl().translate(+offset_x, -offset_x) +
    make_sq(b).align_br().translate(-offset_x, -offset_x)
)
# fmt: on


def appear(d: Diagram) -> Animation:
    return animation(lambda t: empty() if t <= 0.5 else d)


def unveil_triangles():
    anims = [appear(t) for t in ts]
    return constant(sq) + movie_add(anims)


def show_text_1():
    Δ = 0.2
    background = constant(sq + concat(ts))
    # Not great to manually specify the positions of the annotations.
    # Can we get these positions based on the path of the triangle?
    annot_t = (
        annot("a", (offset_x + a / 2, offset_y - Δ))
        + annot("b", (offset_x + a - Δ, offset_y - b / 2))
        + annot("c", (offset_x + a / 2 - Δ, offset_y - b / 2 - Δ / 2))
    )
    return background + splice(appear(annot_t), constant(annot_t) + appear(annot_tl))


def move_triangles():
    background = sq + ts[1] + ts[2] + annot_tl
    # fmt: off
    move_tl = animation(lambda t: ts[0].translate(t * b, t * a) + ts[3])
    move_tr = animation(lambda t: ts[0].translate(b, a) + ts[3].translate(-t * a, t * b))
    # fmt: on
    return constant(background) + splice(move_tl, move_tr)


def regroup_squares():
    background = (
        sq + ts[0].translate(b, a) + ts[1] + ts[2] + ts[3].translate(-a, b) + annot_tl
    )
    return constant(background) + animation(lambda t: sqs_final.fill_opacity(t))


def show_text_2():
    Δ = 0.2
    background = constant(sqs_final + annot_tl)
    annot_t = (
        annot("a", (offset_x - Δ, b / 2))
        + annot("a", (-b / 2, -offset_x + Δ))
        + annot("b", (-offset_x + Δ, a / 2))
        + annot("b", (a / 2, -offset_x + Δ))
    )
    return background + splice(appear(annot_t), constant(annot_t) + appear(annot_tr))


anim = constant(frame) + movie(
    unveil_triangles(),
    show_text_1(),
    move_triangles(),
    regroup_squares(),
    show_text_2(),
)
render_gif(anim, "examples/output/pythagoras.gif", 24)
