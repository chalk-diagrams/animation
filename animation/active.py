"""
An abstraction for time-varying values.
Based on Haskell's active package
https://hackage.haskell.org/package/active-0.1.0.6

which in turn is inspired by

> Kevin Matlage and Andy Gill.
> Every Animation Should Have a Beginning, a Middle, and an End.
> Trends in Functional Programming, 2010.
> http://ku-fpg.github.io/files/Matlage-10-BeginningMiddleEnd.pdf

"""

from dataclasses import dataclass
from typing import Callable, Generic, List, TypeVar

import numpy as np


Time = float
Duration = float

A = TypeVar("A")
B = TypeVar("B")


@dataclass
class Era:
    start: Time
    end: Time

    def duration(self) -> Duration:
        return self.end - self.start


@dataclass
class Active(Generic[A]):
    pass


@dataclass
class Constant(Active, Generic[A]):
    value: A


@dataclass
class Dynamic(Active, Generic[A]):
    era: Era
    func: Callable[[Time], A]


def make_active(start: Time, end: Time, func: Callable[[Time], A]) -> Active[A]:
    return Dynamic(Era(start, end), func)


def on_active(
    f: Callable[[A], B],
    g: Callable[[Dynamic[A]], B],
    active: Active[A],
) -> B:
    match active:
        case Constant(value):
            return f(value)
        case Dynamic(_):
            return g(active)


def interval(start, end) -> Active[Time]:
    return make_active(start, end, lambda t: t)


ui = lambda: interval(0, 1)


def simulate(rate, active: Active[A]) -> List[A]:
    def f(a):
        return [a]

    def g(d):
        s = d.era.start
        e = d.era.end
        steps = np.arange(s, e, 1 / rate)
        return [d.func(t) for t in steps]

    return on_active(f, g, active)
