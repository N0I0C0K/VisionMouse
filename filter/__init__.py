import numpy as np


class SlidingWindowMeanFilter:
    def __init__(self, window_size: int = 12) -> None:
        self.data = np.zeros((window_size, 2))

    def push(self, point: tuple[int, int]) -> tuple[int, int]:
        self.data = np.roll(self.data, -1, 0)
        self.data[-1] = point
        return self.get()

    def get(self) -> tuple[int, int]:
        sx = np.mean(self.data[:, 0])
        sy = np.mean(self.data[:, 1])
        return (int(sx), int(sy))
