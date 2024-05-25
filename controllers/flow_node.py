from typing import Protocol, Any, TypeVar, Generic, NewType, Callable, Iterable
from functools import partial

from controllers.camera import camera
from controllers.types import FrameTuple, Position
from controllers.models import HandInfo
from controllers.landmark import land_mark_model
from controllers.landmark_match import LandMarkMatch
from controllers.cursor_handle import CursorHandleEnum
from controllers.hand_move import hand_move_handler
from utils.iter import min_item

from utils import logger

_Output = TypeVar("_Output")
_InPut = TypeVar("_InPut")

_NoResult = NewType("_NoResult", object)

NoResult: _NoResult = _NoResult(object())


class FlowNode(Protocol, Generic[_InPut, _Output]):
    output: _Output
    next_nodes: list["FlowNode"]
    enable: bool

    def forward(self, _in: _InPut) -> _Output:
        raise NotImplementedError()

    def gen_forward_next(self) -> list[tuple["FlowNode", _Output]]:
        raise NotImplementedError()

    def add_next(self, next: "FlowNode[_Output, Any]"):
        raise NotImplementedError()


class BeginFlowNode(FlowNode[_InPut, _Output]):

    def forward(self) -> _Output:
        raise NotImplementedError


_FlowExecTuple = tuple[FlowNode, _Output]


def run_flow(begin_node: FlowNode[Any, Any], _in=None):
    begin_node.forward(_in)
    next_gen: list[_FlowExecTuple] = begin_node.gen_forward_next()
    while len(next_gen) > 0:
        next_gen = _run_normal_node(next_gen)


def _run_normal_node(node_tuple: list[_FlowExecTuple]) -> list[_FlowExecTuple]:
    res = []
    for next_node, val in node_tuple:
        next_node.forward(val)
        res.extend(next_node.gen_forward_next())
    return res


class FlowNodeBase(FlowNode[_InPut, _Output]):
    def __init__(self) -> None:
        self.output: _NoResult | _Output = NoResult
        self.next_nodes = []
        self.enable = True

    def gen_forward_next(self) -> list[tuple[FlowNode[_Output, Any], _Output]]:
        if self.output is NoResult:
            return []
        return list(
            (next_node, self.output)
            for next_node in self.next_nodes
            if next_node.enable
        )  # type: ignore

    def add_next(self, next: FlowNode[_Output, Any]):
        self.next_nodes.append(next)


class CameraNode(FlowNodeBase[None, FrameTuple]):
    def forward(self, in_: None):
        t = camera.read(auto_open=True)
        self.output = t
        return t


class LandMarkModelNode(FlowNodeBase[FrameTuple, list[HandInfo]]):
    def forward(self, frame_info: FrameTuple) -> list[HandInfo]:
        t = land_mark_model.forward(frame_info)
        self.output = t
        return t


class LandMarkFilterNode(FlowNodeBase[list[HandInfo], HandInfo]):
    def __init__(self):
        super().__init__()
        self.last_hand: HandInfo | None = None

    def forward(self, hand_info_list: list[HandInfo]) -> HandInfo | _NoResult:
        if len(hand_info_list) == 0:
            self.output = NoResult
            return NoResult
        if self.last_hand is None:
            self.last_hand = hand_info_list[0]
            return hand_info_list[0]

        t = min_item(hand_info_list, lambda x: x.distance(self.last_hand))  # type: ignore
        self.output = t
        return t


class CursorMoveHandleNode(FlowNodeBase[HandInfo, Position]):
    def forward(self, hand_info: HandInfo) -> Position:
        pos = hand_move_handler.forward(hand_info)
        self.output = pos
        return pos


class GestureMatchNode(FlowNodeBase[HandInfo, bool]):

    def __init__(self, matcher: LandMarkMatch) -> None:
        super().__init__()
        self.matcher = matcher

    def forward(self, hand_info: HandInfo) -> bool:
        t = self.matcher.match(hand_info)
        self.output = t
        return t


from collections import deque


class PreResultWindowNode(FlowNodeBase[_InPut, _InPut]):
    def __init__(self, n: int, fn: Callable[[Iterable[_InPut]], _InPut]) -> None:
        """
        适用于对于历史数据的处理，比如需要同时满足前面几次输入都为 true 等
        """
        super().__init__()
        self.n = n
        self.pre_result = deque(maxlen=n)
        self.fn = partial(fn, self.pre_result)

    def forward(self, _in: _InPut) -> _InPut:
        self.pre_result.append(_in)
        t = self.fn()
        if len(self.pre_result) < self.n:
            self.output = NoResult
        else:
            self.output = t
        return t


class CursorHandleNode(FlowNodeBase[bool, _NoResult]):
    def __init__(
        self, cursor_move_node: FlowNode[Any, Position], cursor_handle: CursorHandleEnum
    ) -> None:
        super().__init__()
        self.pos_provider = cursor_move_node
        self.cursor_handle = cursor_handle

    def forward(self, _in: bool) -> _NoResult:
        pos = self.pos_provider.output
        if _in:
            logger.info({"tgt": self.cursor_handle.name})
            self.cursor_handle.execute(pos[0], pos[1])  # type: ignore
        return NoResult


from controllers.show_local import show_frame_local, close, draw_circle


class ShowFrameNode(FlowNodeBase[FrameTuple, _NoResult]):
    def forward(self, _in: FrameTuple) -> _NoResult:
        if not show_frame_local(_in.frame):
            self.enable = False
            close()
        return NoResult

    def __del__(self):
        close()


class CombineFlowNode(FlowNodeBase[_InPut, _Output]):
    def __init__(
        self, start: FlowNode[_InPut, Any], end: FlowNode[Any, _Output]
    ) -> None:
        super().__init__()
        self.start = start
        self.end = end

    def forward(self, _in: _InPut) -> _Output:
        run_flow(self.start, _in)
        self.output = self.end.output
        return self.end.output

    def gen_forward_next(self) -> list[tuple[FlowNode[_Output, Any], _Output]]:
        return self.end.gen_forward_next()

    def add_next(self, next: FlowNode[_Output, Any]):
        self.end.add_next(next)


class DrawLandMarkNode(FlowNodeBase[HandInfo, FrameTuple]):
    def __init__(self, camera_node: FlowNode[Any, FrameTuple]) -> None:
        super().__init__()
        self.camera_node = camera_node

    def forward(self, _in: HandInfo) -> FrameTuple:
        frame = self.camera_node.output
        for p in _in.hand_landmark_pos:
            draw_circle(frame.frame, p[0], p[1])
        self.output = frame
        return frame


class LogAnyNode(FlowNodeBase[Any, _NoResult]):
    def forward(self, _in: Any) -> _NoResult:
        logger.info(_in)
        return NoResult
