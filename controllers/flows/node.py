from collections import deque
from functools import partial
from typing import Any, Callable, Generic, Iterable, NewType, Protocol, TypeVar

from controllers.camera import camera
from controllers.cursor_handle import CursorHandleEnum
from controllers.hand_info import HandInfo
from controllers.hand_move import hand_move_handler
from controllers.landmark_match import GestureMatch
from controllers.show_local import close, draw_circle, show_frame_local
from controllers.types import FrameTuple, Position

from controllers.model.landmark import HandLandMarkModel
from controllers.model.landmark_v2 import HandLandMarkModelV2
from controllers.model.gesture import GestureModel, global_gesture_model

from utils import logger
from utils.iter import min_item

_Output = TypeVar("_Output")
_InPut = TypeVar("_InPut")

_NoResult = NewType("_NoResult", object)

NoResult: _NoResult = _NoResult(object())


class FlowNode(Protocol, Generic[_InPut, _Output]):
    output: _Output
    next_nodes: list["FlowNode"]
    enable: bool

    def init(self):
        raise NotImplementedError()

    def forward(self, _in: _InPut) -> _Output:
        raise NotImplementedError()

    def gen_forward_next(self) -> list[tuple["FlowNode", _Output]]:
        raise NotImplementedError()

    def add_next(self, next_node: "FlowNode[_Output, Any]"):
        raise NotImplementedError()

    def clean_effect(self):
        raise NotImplementedError()


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
        self.forward_next = True

    def init(self):
        for next_node in self.next_nodes:
            next_node.init()

    def gen_forward_next(self) -> list[tuple[FlowNode[_Output, Any], _Output]]:
        if self.output is NoResult or not self.forward_next:
            return []
        return list(
            (next_node, self.output)
            for next_node in self.next_nodes
            if next_node.enable
        )  # type: ignore

    def add_next(self, next_node: FlowNode[_Output, Any]):
        self.next_nodes.append(next_node)

    def clean_effect(self):
        for next_node in self.next_nodes:
            next_node.clean_effect()


class CameraNode(FlowNodeBase[None, FrameTuple]):
    def init(self):
        camera.open()
        super().init()

    def forward(self, _):
        t = camera.read()
        self.output = t
        return t

    def clean_effect(self):
        camera.close()
        super().clean_effect()


class LandMarkModelNode(FlowNodeBase[FrameTuple, list[HandInfo]]):
    def __init__(self) -> None:
        super().__init__()
        self.land_mark = None

    def init(self):

        self.land_mark = HandLandMarkModel()

    def forward(self, frame_info: FrameTuple) -> list[HandInfo]:
        assert self.land_mark is not None

        t = self.land_mark.forward(frame_info)
        self.output = t
        return t

    def clean_effect(self):
        assert self.land_mark is not None
        self.land_mark.close()

        super().clean_effect()


class LandMarkFilterNode(FlowNodeBase[list[HandInfo], HandInfo]):
    def __init__(self):
        super().__init__()
        self.last_hand: HandInfo | None = None

    def forward(self, hand_info_list: list[HandInfo]) -> HandInfo | _NoResult:
        l_hand = len(hand_info_list)
        if l_hand == 0:
            self.last_hand = None
            self.output = NoResult
            return NoResult

        if l_hand == 1 or self.last_hand is None:
            self.last_hand = hand_info_list[0]
            self.output = hand_info_list[0]
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

    def __init__(self, matcher: GestureMatch) -> None:
        super().__init__()
        self.matcher = matcher

    def forward(self, hand_info: HandInfo) -> bool:
        t = self.matcher.match(hand_info)
        self.output = t
        return t


_WindowItemType = TypeVar("_WindowItemType")


class PreResultWindowNode(
    FlowNodeBase[_InPut, _Output], Generic[_InPut, _Output, _WindowItemType]
):
    def __init__(
        self,
        n: int,
        fn: Callable[[Iterable[_WindowItemType]], _Output],
        get_item_fn: Callable[[_InPut], _WindowItemType] | None = None,
    ) -> None:
        """
        适用于对于历史数据的处理，比如需要同时满足前面几次输入都为 true 等
        """
        super().__init__()
        self.n = n
        self.pre_result: deque[_WindowItemType] = deque(maxlen=n)
        self.fn = partial(fn, self.pre_result)
        self.get_item_fn = get_item_fn if get_item_fn is not None else lambda x: x

    def forward(self, _in: _InPut) -> _Output:
        self.pre_result.append(self.get_item_fn(_in))
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
        if _in:
            pos = self.pos_provider.output
            logger.info({"tgt": self.cursor_handle.name})
            self.cursor_handle.execute(pos[0], pos[1])  # type: ignore
        return NoResult


class ShowFrameNode(FlowNodeBase[FrameTuple, _NoResult]):
    def forward(self, _in: FrameTuple) -> _NoResult:
        if not show_frame_local(_in.frame):
            self.enable = False
            close()
        return NoResult

    def clean_effect(self):
        close()
        return super().clean_effect()


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

    def add_next(self, next_node: FlowNode[_Output, Any]):
        self.end.add_next(next_node)

    def clean_effect(self):
        self.start.clean_effect()

    def init(self):
        self.start.init()


class DrawLandMarkNode(FlowNodeBase[HandInfo, FrameTuple]):
    def __init__(self, camera_node: FlowNode[Any, FrameTuple]) -> None:
        super().__init__()
        self.camera_node = camera_node

    def forward(self, _in: HandInfo) -> FrameTuple:
        frame = self.camera_node.output
        for p in _in.hand_landmark_pos:
            draw_circle(frame.frame, int(p[0]), int(p[1]))
        self.output = frame
        return frame


class LogAnyNode(FlowNodeBase[Any, _NoResult]):
    def forward(self, _in: Any) -> _NoResult:
        logger.info(_in)
        return NoResult


class LandMarkV2Node(FlowNodeBase[FrameTuple, list[HandInfo]]):
    def __init__(self) -> None:
        super().__init__()
        self.land_mark_v2 = None

    def init(self):
        self.land_mark_v2 = HandLandMarkModelV2()
        super().init()

    def forward(self, _in: FrameTuple) -> list[HandInfo]:
        assert self.land_mark_v2 is not None
        res = self.land_mark_v2.forward(_in)
        self.output = res
        return res

    def clean_effect(self):
        assert self.land_mark_v2 is not None
        self.land_mark_v2.close()
        super().clean_effect()


class GestureRecognizeNode(FlowNodeBase[FrameTuple, list[HandInfo]]):
    def __init__(self) -> None:
        super().__init__()
        self.model = global_gesture_model

    def init(self):
        # self.model = GestureModel()
        super().init()

    def forward(self, _in: FrameTuple) -> list[HandInfo]:
        assert self.model is not None
        res = self.model.forward(_in)
        self.output = res
        return res

    def clean_effect(self):
        assert self.model is not None
        # self.model.close()
        super().clean_effect()
