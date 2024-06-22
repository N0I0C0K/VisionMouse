from dataclasses import dataclass
from typing import Optional

from controllers.landmark_match import GestureMatch
from controllers.hand_info import HandInfo
from controllers.hand_move import hand_move_handler
from controllers.cursor_handle import CursorHandleEnum, current_position
from controllers.flows.window import (
    WindowHandler,
    jump_false,
    jump_true,
    move_down,
    all_true,
    handle_dict,
    move_up,
)
from controllers.flows.node import (
    PreResultWindowNode,
    CombineFlowNode,
    GestureMatchNode,
    CursorHandleNode,
    OperationAndNode,
    OperationMapNode,
)

from utils.types import Position3D


# tuple[GestureMatch, WindowHandler[bool]]
@dataclass
class GestureMatcherCompose:
    gesture_matcher: GestureMatch
    check_func: WindowHandler[bool, bool]
    cursor_handle: CursorHandleEnum
    window_len: int = 3
    move_check: Optional[WindowHandler[Position3D, bool]] = None
    stop_move_cursor_when_active: bool = False

    def __hash__(self) -> int:
        return (
            hash(self.gesture_matcher) ^ hash(self.check_func) ^ hash(self.move_check)
        )


gesture_handle_set: set[GestureMatcherCompose] = {
    GestureMatcherCompose(
        GestureMatch.Index_Thumb, jump_true, CursorHandleEnum.LeftDown
    ),
    GestureMatcherCompose(
        GestureMatch.Index_Thumb, jump_false, CursorHandleEnum.LeftUp
    ),
    GestureMatcherCompose(
        GestureMatch.Middle_Thumb, jump_false, CursorHandleEnum.RightClick
    ),
    GestureMatcherCompose(
        GestureMatch.Victory,
        all_true,
        CursorHandleEnum.ScrollUp,
        move_check=move_down,
        stop_move_cursor_when_active=True,
    ),
    GestureMatcherCompose(
        GestureMatch.Victory,
        all_true,
        CursorHandleEnum.ScrollDown,
        move_check=move_up,
        stop_move_cursor_when_active=True,
    ),
}


def gen_gesture_and_cursor_handle_mapping_list() -> list[dict]:
    res = [
        {
            "match": ges.gesture_matcher.name,
            "matchFunc": ges.check_func.name,
            "handle": ges.cursor_handle.name,
        }
        for ges in gesture_handle_set
    ]
    return res


def set_gesture_and_cursor_handle_mapping(data: list[dict]):
    # if flow_manager.running or _inited:
    #     raise RuntimeError("can not change during running")

    gesture_handle_set.clear()
    for t in data:
        gesture_matcher = GestureMatch[t["match"]]
        match_func = handle_dict[t["matchFunc"]]
        handler = CursorHandleEnum[t["handle"]]
        gesture_handle_set.add(
            GestureMatcherCompose(gesture_matcher, match_func, handler)
        )


def stop_cursor_when_active(_in: bool) -> None:
    if hand_move_handler.enable_move == _in:
        hand_move_handler.enable_move = not _in
        hand_move_handler.last_hand = None


def gen_gesture_and_cursor_combine_node(gesture_matcher: GestureMatcherCompose):
    gesture, fn = gesture_matcher.gesture_matcher, gesture_matcher.check_func

    def get_handinfo_pos(hand: HandInfo) -> Position3D:
        return hand.anchor

    def use_handinfo(hand: HandInfo) -> HandInfo:
        return hand

    begin_node = OperationMapNode(use_handinfo)

    gesture_node = GestureMatchNode(gesture)
    pre_node = PreResultWindowNode(gesture_matcher.window_len, fn)
    cursor_node = CursorHandleNode(current_position, gesture_matcher.cursor_handle)

    begin_node.add_next(gesture_node)
    gesture_node.add_next(pre_node)

    if gesture_matcher.move_check != None:
        get_pos_node = OperationMapNode(get_handinfo_pos)
        pos_window = PreResultWindowNode(6, gesture_matcher.move_check)
        and_node = OperationAndNode([lambda: pre_node.output == True])

        begin_node.add_next(get_pos_node)
        get_pos_node.add_next(pos_window)
        pos_window.add_next(and_node)

        and_node.add_next(cursor_node)

        if gesture_matcher.stop_move_cursor_when_active:
            and_node.add_next(OperationMapNode(stop_cursor_when_active))

    else:
        pre_node.add_next(cursor_node)

    return CombineFlowNode(begin_node, cursor_node)


def gen_all_cursor_control_node():
    for it in gesture_handle_set:
        yield gen_gesture_and_cursor_combine_node(it)
