import sys
from math import sqrt
from enum import Enum
from typing import Protocol
from functools import cache

SYS_PLATFORM = sys.platform

if SYS_PLATFORM.startswith("win32"):
    from pyautogui._pyautogui_win import (
        _moveTo,
        _position,
        _click,
        _mouseDown,
        _mouseUp,
        _vscroll,
    )
elif SYS_PLATFORM.startswith("darwin"):
    from pyautogui._pyautogui_osx import (
        _moveTo,
        _position,
        _click,
        _mouseDown,
        _mouseUp,
        _vscroll,
    )
else:
    raise ImportError

from controllers.types import Position
from utils import distance
from utils.enum import DictEnum


class CursorHandler(Protocol):
    def __call__(self, x: int, y: int):
        raise NotImplementedError


def direction(t: tuple[int, int]) -> tuple[float, float]:
    x, y = t
    dis = sqrt(x * x + y * y)
    return x / dis, y / dis


def current_position() -> Position:
    return _position()


def move(dx: int, dy: int) -> Position:
    pos = _position()
    _moveTo(pos[0] + dx, pos[1] + dy)
    return _position()


# class MoveByHandler(CursorHandler):
#     def __call__(self, dx: int, dy: int):
#         pos = _position()
#         _moveTo(pos[0] + dx, pos[1] + dy)
#         return _position()


class MoveToHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _moveTo(x, y)
        return _position()


class LeftClickHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _mouseDown(x, y, "left")


class RightClickHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _mouseDown(x, y, "right")


class ScrollDownHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _vscroll(-10, x, y)


class ScrollUpHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _vscroll(10, x, y)


class CursorHandleEnum(DictEnum):
    MoveTo = MoveToHandler()
    LeftClick = LeftClickHandler()
    RightClick = RightClickHandler()
    ScrollDown = ScrollDownHandler()
    ScrollUp = ScrollUpHandler()

    def __init__(self, _handler: CursorHandler) -> None:
        self._handler = _handler

    def execute(self, x: int, y: int):
        self._handler(x, y)
