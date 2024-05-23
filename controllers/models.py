from utils.types import Position
from utils import distance


from dataclasses import dataclass, field


@dataclass
class HandInfo:
    hand_landmark_pos: list[Position]
    camera_size: tuple[int, int]
    c_time: float
    _unit: int = field(init=False)

    def __post_init__(self):
        self._unit = distance(self.hand_landmark_pos[0], self.anchor)

    @property
    def anchor(self) -> Position:
        """
        获取中指根部的坐标，作为整个手掌的锚点
        """
        return self.hand_landmark_pos[9]

    @property
    def unit(self) -> int:
        return self._unit

    @property
    def is_pinch(self) -> bool:
        return self.is_touched(4, 8)

    def is_touched(self, idx1: int, idx2: int) -> bool:
        return self.get_mark_distance(idx1, idx2) * 16 < self.unit

    def get_mark_distance(self, mark_idx1: int, mark_idx2: int) -> int:
        return distance(
            self.hand_landmark_pos[mark_idx1], self.hand_landmark_pos[mark_idx2]
        )

    def anchor_diff(self, other: "HandInfo") -> tuple[Position, float]:
        p = self.anchor
        t = other.anchor
        return (p[0] - t[0], p[1] - t[1]), self.c_time - other.c_time
