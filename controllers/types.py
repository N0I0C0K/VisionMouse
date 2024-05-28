import cv2
from typing import NamedTuple, Optional

from pydantic import BaseModel


class FrameTuple(NamedTuple):
    frame: cv2.typing.MatLike
    width: int
    height: int
    ctime: float


class SizeTuple(NamedTuple):
    width: int
    height: int


class CameraState(NamedTuple):
    is_opened: bool
    size: SizeTuple
    exposure: int


Position = tuple[int | float, int | float]


class CameraSettingModel(BaseModel):
    exposure: Optional[int] = None
