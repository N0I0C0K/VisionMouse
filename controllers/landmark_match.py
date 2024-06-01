from typing import Any, Protocol

from controllers.hand_info import HandInfo, LandMark, Gesture

from utils.enum import DictEnum


class BaseMatch(Protocol):
    def __call__(self, hand_info: HandInfo) -> bool:
        raise NotImplementedError

    def __hash__(self) -> int:
        raise NotImplementedError


class LandMarkMatchGen(BaseMatch):
    def __init__(self, lt: LandMark, rt: LandMark) -> None:
        self.lt = lt
        self.rt = rt

    def __call__(self, hand_info: HandInfo) -> bool:
        return hand_info.is_touched(self.lt, self.rt)

    def __hash__(self) -> int:
        return hash(self.lt) ^ hash(self.rt) ^ 1829


class GestureMatchGen(BaseMatch):
    def __init__(self, gesture: Gesture) -> None:
        super().__init__()
        self.gesture = gesture

    def __call__(self, hand_info: HandInfo) -> bool:
        return hand_info.gesture == self.gesture

    def __hash__(self) -> int:
        return hash(self.gesture) ^ 27182


class GestureMatch(DictEnum):
    Index_Thumb = LandMarkMatchGen(LandMark.INDEX_FINGER_TIP, LandMark.THUMB_TIP)
    Middle_Thumb = LandMarkMatchGen(LandMark.MIDDLE_FINGER_TIP, LandMark.THUMB_TIP)
    Ring_Thumb = LandMarkMatchGen(LandMark.RING_FINGER_TIP, LandMark.THUMB_TIP)
    Pinky_Thumb = LandMarkMatchGen(LandMark.PINKY_TIP, LandMark.THUMB_TIP)

    Closed_Fist = GestureMatchGen(Gesture.Closed_Fist)
    Open_Palm = GestureMatchGen(Gesture.Open_Palm)
    Pointing_Up = GestureMatchGen(Gesture.Pointing_Up)
    Thumb_Down = GestureMatchGen(Gesture.Thumb_Down)
    Thumb_Up = GestureMatchGen(Gesture.Thumb_Up)
    Victory = GestureMatchGen(Gesture.Victory)
    ILoveYou = GestureMatchGen(Gesture.ILoveYou)

    def __init__(self, func: BaseMatch) -> None:
        super().__init__()
        self.func = func

    def match(self, hand_info: HandInfo) -> bool:
        return self.func(hand_info)
