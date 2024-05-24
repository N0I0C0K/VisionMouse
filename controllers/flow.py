from typing import Any
from controllers.flow_node import (
    FlowNode,
    hands_handle_node,
    hands_filter_node,
    camera_node,
    land_mark_model_node,
    cursor_move_handle_node,
    _FlowExecTuple,
    show_frame_node,
)


def run_flow(begin_node: FlowNode[None, Any]):
    begin_node.forward(None)
    next_gen: list[_FlowExecTuple] = begin_node.gen_forward_next()
    while len(next_gen) > 0:
        next_gen = _run_normal_node(next_gen)


def _run_normal_node(node_tuple: list[_FlowExecTuple]) -> list[_FlowExecTuple]:
    res = []
    for next_node, val in node_tuple:
        next_node.forward(val)
        res.extend(next_node.gen_forward_next())
    return res


def init_graph():
    camera_node.add_next(land_mark_model_node)
    camera_node.add_next(show_frame_node)

    land_mark_model_node.add_next(hands_filter_node)

    hands_filter_node.add_next(cursor_move_handle_node)

    cursor_move_handle_node.add_next(hands_handle_node)


init_graph()


def start_flow():
    run_flow(camera_node)
