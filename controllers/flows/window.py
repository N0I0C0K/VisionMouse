from typing import Generic, Iterable, Protocol, TypeVar

from controllers.hand_info import HandInfo

T = TypeVar("T")
P = TypeVar("P")


class WindowHandler(Protocol, Generic[T]):
    name: str

    def __call__(self, it: Iterable[T]) -> T: ...


class ComplexWindowHandler(WindowHandler[T], Generic[T, P]):
    def __call__(self, it: Iterable[T]) -> P: ...


def _all(it: Iterable[bool]) -> bool:
    return all(it)


def _all_not(it: Iterable[bool]) -> bool:
    return all(not i for i in it)


class JumpTrue(WindowHandler[bool]):
    name = "JumpTrue"

    def __call__(self, it: Iterable[bool]) -> bool:
        it = iter(it)
        return not next(it) and _all(it)


jump_true = JumpTrue()


class JumpFalse(WindowHandler[bool]):
    name = "JumpFalse"

    def __call__(self, it: Iterable[bool]) -> bool:
        it = iter(it)
        return next(it) and _all_not(it)


jump_false = JumpFalse()


class AllTrue(WindowHandler[bool]):
    name = "AllTrue"

    def __call__(self, it: Iterable[bool]) -> bool:
        return _all(it)


all_true = AllTrue()


class MoveDonw(ComplexWindowHandler[tuple[bool, HandInfo], bool]):
    name = "MoveDown"

    def __call__(self, it: Iterable[tuple[bool, HandInfo]]) -> bool:
        ite = iter(it)
        first_pos = next(ite)[1].anchor
        end_pos = first_pos
        for i in ite:
            end_pos = i[1].anchor

        return end_pos[1] < first_pos[1]


move_down = MoveDonw()

handle_dict: dict[str, "WindowHandler"] = {}


def _add_handle(handle: WindowHandler):
    handle_dict[handle.name] = handle


_add_handle(jump_false)
_add_handle(jump_true)
_add_handle(all_true)
