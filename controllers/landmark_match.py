from typing import Any, Protocol

from controllers.hand_info import HandInfo, LandMark
from utils.enum import DictEnum

from enum import Enum


class BaseMatch(Protocol):
    def __call__(self, hand_info: HandInfo) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError


class MatchGen(BaseMatch):
    def __init__(self, lt: LandMark, rt: LandMark) -> None:
        self.lt = lt
        self.rt = rt

    def __call__(self, hand_info: HandInfo) -> bool:
        return hand_info.is_touched(self.lt, self.rt)

    def __hash__(self) -> int:
        return hash(self.lt) ^ hash(self.rt)


class LandMarkMatch(DictEnum):
    Index_Thumb = MatchGen(LandMark.INDEX_FINGER_TIP, LandMark.THUMB_TIP)
    Middle_Thumb = MatchGen(LandMark.MIDDLE_FINGER_TIP, LandMark.THUMB_TIP)
    Ring_Thumb = MatchGen(LandMark.RING_FINGER_TIP, LandMark.THUMB_TIP)
    Pinky_Thumb = MatchGen(LandMark.PINKY_TIP, LandMark.THUMB_TIP)

    def __init__(self, func: BaseMatch) -> None:
        super().__init__()
        self.func = func

    def match(self, hand_info: HandInfo) -> bool:
        return self.func(hand_info)
