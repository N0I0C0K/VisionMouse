import numpy as np
import typing

T = typing.TypeVar("T", int, float)


class SlidingWindowMeanFilter(typing.Generic[T]):
    def __init__(
        self,
        window_size: int = 12,
    ) -> None:
        self.data = np.zeros((window_size, 2))
        self.idx = 0
        self.window_size = window_size
        self.size = 0

    def push(self, point: tuple[T, T]) -> tuple[float, float]:
        self.data[self.idx] = point
        self.size = min(self.size + 1, self.window_size)
        pos = self.get()
        self.idx = (self.idx + 1) % self.window_size
        return pos

    def get(self) -> tuple[float, float]:
        if self.size * 2 >= self.window_size:
            sx = np.mean(self.data[:, 0])
            sy = np.mean(self.data[:, 1])
            return (sx.astype(float), sy.astype(float))
        else:
            return self.data[self.idx]


class StepFilter(typing.Generic[T]):
    def __init__(self, smooth: float = 4) -> None:
        self.last_pos: tuple[float, float] = (0, 0)
        self.smooth = smooth

    def push(self, point: tuple[T, T]) -> tuple[float, float]:
        lp = self.last_pos
        dx, dy = point[0] - lp[0], point[1] - lp[1]
        tx, ty = lp[0] + dx / self.smooth, lp[1] + dy / self.smooth
        self.last_pos = (tx, ty)
        return (tx, ty)
