from typing import Any, Iterable, TypeVar, Callable

from controllers.flow_node import (
    CameraNode,
    CursorMoveHandleNode,
    FlowNode,
    LandMarkFilterNode,
    LandMarkModelNode,
    ShowFrameNode,
    _FlowExecTuple,
    PreResultWindowNode,
    CombineFlowNode,
    GestureMatchNode,
    CursorHandleNode,
    DrawLandMarkNode,
    run_flow,
)
from controllers.landmark_match import LandMarkMatch
from controllers.cursor_handle import CursorHandleEnum

T = TypeVar("T")

camera_node = CameraNode()

land_mark_model_node = LandMarkModelNode()
hands_filter_node = LandMarkFilterNode()
cursor_move_handle_node = CursorMoveHandleNode()
show_frame_node = ShowFrameNode()
draw_node = DrawLandMarkNode(camera_node)


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


GestureCursorGen = tuple[
    LandMarkMatch, Callable[[Iterable[bool]], bool], CursorHandleEnum
]

gesture_and_cursor_handle_list: list[GestureCursorGen] = [
    (LandMarkMatch.Index_Thumb, _jump_true, CursorHandleEnum.LeftDown),
    (LandMarkMatch.Index_Thumb, _jump_false, CursorHandleEnum.LeftUp),
    (LandMarkMatch.Middle_Thumb, _jump_true, CursorHandleEnum.RightClick),
]


def gen_gesture_and_cursor_combine_node(gesture_and_cursor: GestureCursorGen):
    gesture, fn, cursor_handle = gesture_and_cursor
    pre_node = PreResultWindowNode(2, fn)
    gesture_node = GestureMatchNode(gesture)
    cursor_node = CursorHandleNode(cursor_move_handle_node, cursor_handle)

    gesture_node.add_next(pre_node)
    pre_node.add_next(cursor_node)

    return CombineFlowNode(gesture_node, cursor_node)


def init_graph():
    camera_node.add_next(land_mark_model_node)

    land_mark_model_node.add_next(hands_filter_node)

    hands_filter_node.add_next(cursor_move_handle_node)

    hands_filter_node.add_next(draw_node)

    draw_node.add_next(show_frame_node)

    for it in gesture_and_cursor_handle_list:
        hands_filter_node.add_next(gen_gesture_and_cursor_combine_node(it))


init_graph()


def start_flow():
    run_flow(camera_node)
