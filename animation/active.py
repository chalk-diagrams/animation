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

from typing import Callable, Generic, List, Optional, Tuple, TypeVar
from dataclasses import dataclass
from functools import reduce

from chalk.monoid import Monoid

import numpy as np


Time = float
Duration = float

A = TypeVar("A")
B = TypeVar("B")
M = TypeVar("M", bound=Monoid)


@dataclass
class Era:
    start: Time
    end: Time

    @property
    def duration(self) -> Duration:
        return self.end - self.start

    def __add__(self, other: "Era") -> "Era":
        s = min(self.start, other.start)
        e = max(self.end, other.end)
        return Era(s, e)


@dataclass
class Active(Generic[A]):
    def __add__(self, other: "Active[A]") -> "Active[A]":
        return add(self, other)

    def map(self, f: Callable[[A], B]) -> "Active[B]":
        print(self)
        return map(self, f)


@dataclass
class Constant(Active, Generic[A]):
    value: A


@dataclass
class Dynamic(Active, Generic[A]):
    era: Era
    func: Callable[[Time], A]


def map(a: Active[A], f: Callable[[A], B]) -> Active[B]:
    match a:
        case Constant(v):
            return Constant(f(v))
        case Dynamic(e, g):
            return Dynamic(e, lambda t: f(g(t)))


def product(a1: Active[A], a2: Active[B]) -> Active[Tuple[A, B]]:
    pass
    # match (a1, a2):
    #     case (Constant(v1), Constant(v2)):
    #         return Constant((v1, v2))
    #     case (Constant(v1), Dynamic(e2, f2)):
    #         return Dynamic(e2, lambda t: (v1, f2(t)))
    #     case (Dynamic(e1, f1), Constant(v2)):
    #         return Dynamic(e1, lambda t: (f1(t), v2))
    #     case (Dynamic(e1, f1), Dynamic(e2, f2)):
    #         return Dynamic(e1 + e2, lambda t: (f1(t), f2(t)))


def map_with_time(a: Active[A], f: Callable[[Time, A], B]) -> Active[B]:
    match a:
        case Constant(v):
            # Should we avoid this branch?
            return Constant(f(0, v))
        case Dynamic(e, g):
            return Dynamic(e, lambda t: f(t, g(t)))


def add(a1: Active[M], a2: Active[M]) -> Active[M]:
    match (a1, a2):
        case (Constant(v1), Constant(v2)):
            return Constant(v1 + v2)
        case (Constant(v1), Dynamic(e2, f2)):
            return Dynamic(e2, lambda t: v1 + f2(t))
        case (Dynamic(e1, f1), Constant(v2)):
            return Dynamic(e1, lambda t: f1(t) + v2)
        case (Dynamic(e1, f1), Dynamic(e2, f2)):
            return Dynamic(e1 + e2, lambda t: f1(t) + f2(t))


def make_active(start: Time, end: Time, func: Callable[[Time], A]) -> Active[A]:
    return Dynamic(Era(start, end), func)


def get_era(active: Active[A]) -> Optional[Era]:
    match active:
        case Constant(_):
            return None
        case Dynamic(era, _):
            return era


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
identity = lambda a: a


def shift(active: Active[A], offset: Duration) -> Active[A]:
    def g(d: Dynamic[A]) -> Active[A]:
        s_new = d.era.start + offset
        e_new = d.era.end + offset
        func_new = lambda t: d.func(t - offset)
        return make_active(s_new, e_new, func_new)

    return on_active(identity, g, active)


def stretch(active: Active[A], factor: float) -> Active[A]:
    def g(d: Dynamic[A]) -> Active[A]:
        s = d.era.start
        s_new = s
        e_new = s + factor * d.era.duration
        func_new = lambda t: d.func(s + (t - s) / factor)
        return make_active(s_new, e_new, func_new)

    return on_active(identity, g, active)


def trim_before(active: Active[M], M_type: type[M]) -> Active[M]:
    def g(d: Dynamic[M]) -> Active[M]:
        s = d.era.start
        e = d.era.end
        def func_new(t):
            if t < s:
                return M_type.empty()
            else:
                return d.func(t)
        return make_active(s, e, func_new)

    return on_active(identity, g, active)


def trim_after(active: Active[M], M_type: type[M]) -> Active[M]:
    def g(d: Dynamic[M]) -> Active[M]:
        s = d.era.start
        e = d.era.end
        def func_new(t):
            if t > e:
                return M_type.empty()
            else:
                return d.func(t)
        return make_active(s, e, func_new)

    return on_active(identity, g, active)


def at_time(active: Active[A], t: Time) -> Active[A]:
    era = get_era(active)
    if era is None:
        return active
    else:
        return shift(active, t - era.start)


def after(a1: Active[A], a2: Active[A]) -> Active[A]:
    """Shifts `a1` to start at the end of `a2`. Note that `a2` is not contained
    in the resulting `Active`.
    
    """
    era = get_era(a2)
    if era is None:
        return a1
    else:
        return at_time(a1, era.end)


def sequence_add(a1: Active[M], a2: Active[M]) -> Active[M]:
    """Sequences two `Active`s in time and overlays them with the `Monoid`'s
    `__add__` operation.
    
    """
    return a1 + after(a2, a1)


def movie_add(actives: List[Active[M]]) -> Active[M]:
    return reduce(sequence_add, actives)


def splice(a1: Active[A], a2: Active[A]) -> Active[A]:
    """Much uglier than the Haskell version `|>>`."""
    a2_new = after(a2, a1)
    match (a1, a2_new):
        case (Dynamic(e1, f1), Dynamic(e2, f2)):
            def func_new(t):
                if t < e1.end:
                    return f1(t)
                else:
                    return f2(t)
            return Dynamic(e1 + e2, func_new)
        case _:
            return a1 + a2_new


def movie(*actives: Active[A]) -> Active[A]:
    return reduce(splice, actives)


def simulate(rate, active: Active[A]) -> List[A]:
    def f(a: A) -> List[A]:
        return [a]

    def g(d: Dynamic[A]) -> List[A]:
        s = d.era.start
        e = d.era.end
        steps = np.arange(s, e, 1 / rate)
        return [d.func(t) for t in steps]

    return on_active(f, g, active)
