import sys
import secrets
import time

from math import sqrt
from typing import Protocol, Callable, Any

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

from utils.enum import DictEnum

CursorPosition = tuple[int, int]


class CursorHandler(Protocol):
    def __call__(self, x: int, y: int):
        raise NotImplementedError


def safe_division(a, b) -> float:
    return a / b if b != 0 else a / 0.1


def current_position() -> CursorPosition:
    return _position()


def move(dx: int, dy: int) -> CursorPosition:
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


class LeftButtonHandler:
    def __init__(self) -> None:
        self._down = False

    def down(self, x: int, y: int):
        if not self._down:
            _mouseDown(x, y, "left")
            self._down = True

    def up(self, x: int, y: int):
        if self._down:
            _mouseUp(x, y, "left")
            self._down = False


left_button_handler = LeftButtonHandler()


class LeftButtonDownHandler(CursorHandler):
    def __init__(self, handler: LeftButtonHandler) -> None:
        self.handler = handler

    def __call__(self, x: int, y: int):
        self.handler.down(x, y)


class LeftButtonUpHandler(CursorHandler):
    def __init__(self, handler: LeftButtonHandler) -> None:
        self.handler = handler

    def __call__(self, x: int, y: int):
        self.handler.up(x, y)


class LeftClickHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _click(x, y, "left")


class RightClickHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _click(x, y, "right")


class ScrollDownHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _vscroll(-10, x, y)


class ScrollUpHandler(CursorHandler):
    def __call__(self, x: int, y: int):
        _vscroll(10, x, y)


HandleCallback = Callable[[str, CursorPosition, float], None]

on_cursor_handle_execute: dict[str, HandleCallback] = dict()


def add_on_handle_execute(func: HandleCallback) -> Callable[[], Any]:
    key = secrets.token_hex(8)
    on_cursor_handle_execute[key] = func
    return lambda: on_cursor_handle_execute.pop(key)


class CursorHandleEnum(DictEnum):
    MoveTo = MoveToHandler()
    LeftClick = LeftClickHandler()
    RightClick = RightClickHandler()
    ScrollDown = ScrollDownHandler()
    ScrollUp = ScrollUpHandler()
    LeftDown = LeftButtonDownHandler(left_button_handler)
    LeftUp = LeftButtonUpHandler(left_button_handler)

    def __init__(self, _handler: CursorHandler) -> None:
        self._handler = _handler

    def execute(self, x: int, y: int):
        self._handler(x, y)
        for func in on_cursor_handle_execute.values():
            func(self.name, (x, y), time.time())
