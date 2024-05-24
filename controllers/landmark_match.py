from typing import Any, Protocol

from controllers.models import HandInfo, LandMark
from utils.enum import DictEnum

from enum import Enum


class BaseMatch(Protocol):
    def __call__(self, hand_info: HandInfo) -> bool:
        raise NotImplementedError


def gen_match(lt: LandMark, rt: LandMark) -> BaseMatch:
    def match(hand_info: HandInfo) -> bool:
        return hand_info.is_touched(lt, rt)

    return match


class LandMarkMatch(DictEnum):
    Index_Thumb = gen_match(LandMark.THUMB_TIP, LandMark.INDEX_FINGER_TIP)
    Middle_Thumb = gen_match(LandMark.MIDDLE_FINGER_TIP, LandMark.INDEX_FINGER_TIP)
    Ring_Thumb = gen_match(LandMark.RING_FINGER_TIP, LandMark.INDEX_FINGER_TIP)
    Pinky_Thumb = gen_match(LandMark.PINKY_TIP, LandMark.INDEX_FINGER_TIP)

    def __init__(self, func: BaseMatch) -> None:
        self.func = func

    def match(self, hand_info: HandInfo) -> bool:
        return self.func(hand_info)
