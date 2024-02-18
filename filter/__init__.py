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
