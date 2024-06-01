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


class PositionTuple(NamedTuple):
    x: float | int
    y: float | int


class CameraSettingModel(BaseModel):
    exposure: Optional[int] = None


class MouseStateModel(BaseModel):
    baseSpeed: Optional[float] = None
    acceleration: Optional[float] = None


class FlowConnectItemModel(BaseModel):
    match: str
    matchFunc: str
    handle: str


class FlowConnectModel(BaseModel):
    data: list[FlowConnectItemModel]
