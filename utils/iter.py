from typing import Iterable, TypeVar, Callable, Any


T = TypeVar("T")


def min_item(it: Iterable[T], calc: Callable[[T], Any]) -> T:
    res, m = None, None
    for t in it:
        t_m = calc(t)
        if m is None or t_m < m:
            m = t_m
            res = t
    if res is None:
        raise RuntimeError
    return res
