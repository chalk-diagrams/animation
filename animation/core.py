from typing import Callable

from chalk.types import Diagram
from animation.active import Active, Constant, Dynamic, Era, Time, simulate

import imageio


Animation = Active[Diagram]


def constant(diagram: Diagram) -> Animation:
    return Constant(diagram)


def animation(func: Callable[[Time], Diagram], start=0, end=1) -> Animation:
    return Dynamic(Era(start, end), func)


def render_gif(active: Animation, path: str, rate: float) -> None:
    path_frame = "/tmp/frame.png"
    with imageio.get_writer(path, mode="I", fps=rate) as writer:
        for frame in simulate(rate, active):
            frame.render_png(path_frame)
            image = imageio.imread(path_frame)
            writer.append_data(image)
