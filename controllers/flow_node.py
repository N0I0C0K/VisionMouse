from typing import Protocol, Any, TypeVar, Generic, NewType

from controllers.camera import camera
from controllers.types import FrameTuple, Position
from controllers.models import HandInfo
from controllers.landmark import land_mark_model
from controllers.landmark_match import LandMarkMatch
from controllers.cursor_handle import CursorHandleEnum
from controllers.hand_move import hand_move_handler
from utils.iter import min_item

_Output = TypeVar("_Output")
_InPut = TypeVar("_InPut")

_NoResult = NewType("_NoResult", object)

NoResult: _NoResult = _NoResult(object())


class FlowNode(Protocol, Generic[_InPut, _Output]):
    output: _Output | _NoResult
    next_nodes: list["FlowNode"]
    enable: bool

    def forward(self, _in: _InPut) -> _Output:
        raise NotImplementedError()

    def gen_forward_next(self) -> list[tuple["FlowNode", Any]]:
        raise NotImplementedError()

    def add_next(self, next: "FlowNode[_Output, Any]"):
        raise NotImplementedError()


class BeginFlowNode(FlowNode[_InPut, _Output]):

    def forward(self) -> _Output:
        raise NotImplementedError


_FlowExecTuple = tuple[FlowNode, Any]


class FlowNodeBase(FlowNode[_InPut, _Output]):
    def __init__(self) -> None:
        self.output: _NoResult | _Output = NoResult
        self.next_nodes = []
        self.enable = True

    def gen_forward_next(self) -> list[_FlowExecTuple]:
        if self.output is NoResult:
            return []
        return list(
            (next_node, self.output)
            for next_node in self.next_nodes
            if next_node.enable
        )

    def add_next(self, next: FlowNode[_Output, Any]):
        self.next_nodes.append(next)


class CameraNode(FlowNodeBase[None, FrameTuple]):
    def forward(self, in_: None):
        t = camera.read(auto_open=True)
        self.output = t
        return t


camera_node = CameraNode()


class LandMarkModelNode(FlowNodeBase[FrameTuple, list[HandInfo]]):
    def forward(self, frame_info: FrameTuple) -> list[HandInfo]:
        t = land_mark_model.forward(frame_info)
        self.output = t
        return t


land_mark_model_node = LandMarkModelNode()


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


hands_filter_node = LandMarkFilterNode()


class CursorMoveHandleNode(FlowNodeBase[HandInfo, Position]):
    def forward(self, hand_info: HandInfo) -> Position:
        pos = hand_move_handler.forward(hand_info)
        self.output = pos
        return pos


cursor_move_handle_node = CursorMoveHandleNode()


class HandsHandleNode(FlowNodeBase[Position, _NoResult]):
    land_match_and_action_mapping: dict[LandMarkMatch, CursorHandleEnum] = {
        LandMarkMatch.Index_Thumb: CursorHandleEnum.LeftClick
    }

    def __init__(self, land_mark_node: LandMarkFilterNode) -> None:
        super().__init__()
        self.land_mark_node = land_mark_node

    def forward(self, pos: Position) -> _NoResult:
        hand_info = self.land_mark_node.output
        if hand_info is NoResult:
            raise RuntimeError("The attached node must precede self")
        for key, action in self.land_match_and_action_mapping.items():
            if key.match(hand_info):  # type: ignore
                action.execute(pos[0], pos[1])
        return NoResult


hands_handle_node = HandsHandleNode(hands_filter_node)


from controllers.show_local import show_frame_local, close


class ShowFrameNode(FlowNodeBase[FrameTuple, _NoResult]):
    def forward(self, _in: FrameTuple) -> _NoResult:
        if not show_frame_local(_in.frame):
            self.enable = False
            close()
        return NoResult

    def __del__(self):
        close()


show_frame_node = ShowFrameNode()
