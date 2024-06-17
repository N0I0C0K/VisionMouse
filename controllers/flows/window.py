from typing import Generic, Iterable, Protocol, TypeVar, Callable

from controllers.hand_info import Position3D, distance_nd

T = TypeVar("T")
P = TypeVar("P")


class WindowHandler(Generic[T, P]):
    name: str

    def __call__(self, it: Iterable[T]) -> P: ...


handle_dict: dict[str, "WindowHandler"] = {}


class WindowHandlerBase(WindowHandler[T, P]):
    def __init__(self, name: str = "") -> None:
        if name == "":
            name = type(self).__name__
        self.name = name
        handle_dict[self.name] = self

    def __hash__(self) -> int:
        return id(self.name)


class FuncWindowHandler(WindowHandlerBase[T, P]):
    def __init__(self, func: Callable[[Iterable[T]], P], name: str = "") -> None:
        if name == "":
            name = func.__name__
        super().__init__(name)
        self.func = func

    def __call__(self, it: Iterable[T]) -> P:
        return self.func(it)


def _all(it: Iterable[bool]) -> bool:
    return all(it)


def _all_not(it: Iterable[bool]) -> bool:
    return all(not i for i in it)


def _jump_true(it: Iterable[bool]) -> bool:
    it = iter(it)
    return not next(it) and _all(it)


def _jump_false(it: Iterable[bool]) -> bool:
    it = iter(it)
    return next(it) and _all_not(it)


def _move_dir(
    dir: tuple[int, int], min_dis: float = 5
) -> Callable[[Iterable[Position3D]], bool]:
    def warp(it: Iterable[Position3D]) -> bool:
        ite = iter(it)
        first_pos = next(ite)
        end_pos = first_pos
        for i in ite:
            end_pos = i
            diff = (
                end_pos[0] - first_pos[0],
                end_pos[1] - first_pos[1],
            )
            if (dir[0] != 0 and diff[0] * dir[0] <= 0) or (
                dir[1] != 0 and diff[1] * dir[1] <= 0
            ):
                return False
        return distance_nd(end_pos, first_pos) >= min_dis

    return warp


jump_true = FuncWindowHandler(_jump_true, "JumpTrue")
jump_false = FuncWindowHandler(_jump_false, "JumpFalse")
all_true = FuncWindowHandler(_all, "AllTrue")
move_down = FuncWindowHandler(_move_dir((0, -1)), "MoveDown")
move_up = FuncWindowHandler(_move_dir((0, 1)), "MoveUp")


# def _add_handle(handle: WindowHandler):
#     handle_dict[handle.name] = handle


# _add_handle(jump_false)
# _add_handle(jump_true)
# _add_handle(all_true)
