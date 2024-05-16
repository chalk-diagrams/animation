from typing import Callable

from chalk import Diagram
from animation.active import Time, make_active, simulate

import imageio


class Animation:
    def __init__(self, start: Time, end: Time, func: Callable[[Time], Diagram]):
        self.active = make_active(start, end, func)

    def render_gif(self, path: str, rate: float):
        path_frame = "/tmp/frame.png"
        with imageio.get_writer(path, mode="I") as writer:
            for frame in simulate(rate, self.active):
                frame.render_png(path_frame)
                image = imageio.imread(path_frame)
                writer.append_data(image)
