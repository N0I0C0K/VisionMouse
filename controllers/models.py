from dataclasses import dataclass, field
from typing_extensions import Self

from utils import distance
from utils.types import Position
from utils.enum import DictEnum


class LandMark(DictEnum):
    WRIST = 0
    THUMB_CMC = 1
    THUMB_MCP = 2
    THUMB_IP = 3
    THUMB_TIP = 4
    INDEX_FINGER_MCP = 5
    INDEX_FINGER_PIP = 6
    INDEX_FINGER_DIP = 7
    INDEX_FINGER_TIP = 8
    MIDDLE_FINGER_MCP = 9
    MIDDLE_FINGER_PIP = 10
    MIDDLE_FINGER_DIP = 11
    MIDDLE_FINGER_TIP = 12
    RING_FINGER_MCP = 13
    RING_FINGER_PIP = 14
    RING_FINGER_DIP = 15
    RING_FINGER_TIP = 16
    PINKY_MCP = 17
    PINKY_PIP = 18
    PINKY_DIP = 19
    PINKY_TIP = 20


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

    def is_touched(self, lt: LandMark, rt: LandMark) -> bool:
        return self.get_mark_distance(lt, rt) * 16 < self.unit

    def get_mark_distance(self, lt: LandMark, rt: LandMark) -> int:
        return distance(
            self.hand_landmark_pos[lt.value], self.hand_landmark_pos[rt.value]
        )

    def anchor_diff(self, other: "HandInfo") -> tuple[Position, float]:
        p = self.anchor
        t = other.anchor
        return (p[0] - t[0], p[1] - t[1]), self.c_time - other.c_time

    def distance(self, other: Self) -> int:
        return distance(self.anchor, other.anchor)
