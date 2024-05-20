from typing import Callable

from chalk.types import Diagram
from animation.active import Active, Constant, Dynamic, Era, Time, simulate

import imageio


Animation = Active[Diagram]


def constant(diagram: Diagram) -> Animation:
    return Constant(diagram)


def animation(func: Callable[[Time], Diagram], start=0, end=1) -> Animation:
    return Dynamic(Era(start, end), func)


def render_gif(active: Animation, path: str, rate: float, **kwargs) -> None:
    path_frame = "/tmp/frame-{:d}.png"
    with imageio.get_writer(path, fps=rate, **kwargs) as writer:
        for i, frame in enumerate(simulate(rate, active)):
            path = path_frame.format(i)
            frame.render_png(path)
            image = imageio.imread(path)
            writer.append_data(image)
