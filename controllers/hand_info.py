from enum import IntEnum
from math import sqrt

from dataclasses import dataclass, field
from typing_extensions import Self


from utils import distance
from utils.types import Position, Position3D


class LandMark(IntEnum):
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


class Gesture(IntEnum):
    Unknown = 0
    Closed_Fist = 1
    Open_Palm = 2
    Pointing_Up = 3
    Thumb_Down = 4
    Thumb_Up = 5
    Victory = 6
    ILoveYou = 7


def distance_nd(pos1: tuple[float | int, ...], pos2: tuple[float | int, ...]):
    res = 0
    for t1, t2 in zip(pos1, pos2):
        res += (t2 - t1) * (t2 - t1)
    return sqrt(res)


@dataclass
class HandInfo:
    hand_landmark_pos: list[Position3D]
    camera_size: tuple[int, int]
    c_time: float
    gesture: Gesture | None = None
    _unit: float = field(init=False)

    def __post_init__(self):
        self._unit = distance_nd(self.hand_landmark_pos[0], self.anchor)

    @property
    def anchor(self) -> Position3D:
        """
        获取中指根部的坐标，作为整个手掌的锚点
        """
        return self.hand_landmark_pos[9]

    @property
    def unit(self) -> float:
        return self._unit

    def is_touched(self, lt: LandMark, rt: LandMark) -> bool:
        return self.get_mark_distance(lt, rt) * 2.5 < self.unit

    def get_mark_distance(self, lt: LandMark, rt: LandMark) -> float:
        return distance_nd(
            self.hand_landmark_pos[lt.value], self.hand_landmark_pos[rt.value]
        )

    def anchor_diff(self, other: "HandInfo") -> tuple[Position, float]:
        p = self.anchor
        t = other.anchor
        return (p[0] - t[0], p[1] - t[1]), self.c_time - other.c_time

    def distance(self, other: Self) -> float:
        return distance_nd(self.anchor, other.anchor)

    def encode_pos(self) -> str:
        return "/".join(map(lambda x: f"{x[0]},{x[1]}", self.hand_landmark_pos))
