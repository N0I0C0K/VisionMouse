import numpy as np
import typing

T = typing.TypeVar("T")


class SlidingWindowMeanFilter(typing.Generic[T]):
    def __init__(self, window_size: int = 12) -> None:
        self.data = np.zeros((window_size, 2))
        self.idx = 0
        self.window_size = window_size
        self.size = 0

    def push(self, point: tuple[T, T]) -> tuple[T, T]:
        self.data[self.idx] = point
        self.idx = (self.idx + 1) % self.window_size
        self.size = min(self.size + 1, self.window_size)
        return self.get()

    def get(self) -> tuple[T, T]:
        if self.size * 2 >= self.window_size:
            sx = np.mean(self.data[:, 0])
            sy = np.mean(self.data[:, 1])
            return (sx.astype(float), sy.astype(float))
        else:
            return self.data[self.idx]
