import asyncio
import time
from typing import Any, Iterable, TypeVar, Callable, Protocol, Generic

from controllers.flows.node import (
    CameraNode,
    CursorMoveHandleNode,
    FlowNode,
    LandMarkFilterNode,
    LandMarkModelNode,
    LandMarkV2Node,
    GestureRecognizeNode,
    ShowFrameNode,
    PreResultWindowNode,
    CombineFlowNode,
    GestureMatchNode,
    CursorHandleNode,
    DrawLandMarkNode,
    run_flow,
    NoResult,
)
from controllers.landmark_match import GestureMatch
from controllers.cursor_handle import CursorHandleEnum

from utils import config, logger
from utils.threading import set_thread_priority_to_high

T = TypeVar("T")

camera_node = CameraNode()

land_mark_model_node = GestureRecognizeNode()
hands_filter_node = LandMarkFilterNode()
cursor_move_handle_node = CursorMoveHandleNode()
show_frame_node = ShowFrameNode()
draw_node = DrawLandMarkNode(camera_node)


class WindowHandler(Protocol, Generic[T]):
    name: str

    def __call__(self, it: Iterable[T]) -> T: ...


def _all(it: Iterable[bool]) -> bool:
    return all(it)


def _all_not(it: Iterable[bool]) -> bool:
    return all(not i for i in it)


class JumpTrue(WindowHandler[bool]):
    name = "JumpTrue"

    def __call__(self, it: Iterable[bool]) -> bool:
        it = iter(it)
        return not next(it) and _all(it)


_jump_true = JumpTrue()


class JumpFalse(WindowHandler[bool]):
    name = "JumpFalse"

    def __call__(self, it: Iterable[bool]) -> bool:
        it = iter(it)
        return next(it) and _all_not(it)


_jump_false = JumpFalse()

GestureMatcher = tuple[GestureMatch, WindowHandler[bool]]

gesture_and_cursor_handle_mapping: dict[GestureMatcher, CursorHandleEnum] = {
    (GestureMatch.Index_Thumb, _jump_true): CursorHandleEnum.LeftDown,
    (GestureMatch.Index_Thumb, _jump_false): CursorHandleEnum.LeftUp,
    (GestureMatch.Middle_Thumb, _jump_true): CursorHandleEnum.RightClick,
}


def gen_gesture_and_cursor_handle_mapping_list() -> list[dict]:
    res = [
        {"match": ges[0].name, "matchFunc": ges[1].name, "handle": cur.name}
        for ges, cur in gesture_and_cursor_handle_mapping.items()
    ]
    return res


def set_gesture_and_cursor_handle_mapping(data: list[dict]):
    if flow_manager.running or _inited:
        raise RuntimeError("can not change during running")

    gesture_and_cursor_handle_mapping.clear()
    for t in data:
        gesture_matcher = GestureMatch[t["match"]]
        match_func = _jump_false if t["matchFunc"] == "JumpFalse" else _jump_true
        handler = CursorHandleEnum[t["handle"]]
        gesture_and_cursor_handle_mapping[(gesture_matcher, match_func)] = handler


def gen_gesture_and_cursor_combine_node(
    gesture_matcher: GestureMatcher, cursor_handle: CursorHandleEnum
):
    gesture, fn = gesture_matcher
    gesture_node = GestureMatchNode(gesture)
    pre_node = PreResultWindowNode(2, fn)
    cursor_node = CursorHandleNode(cursor_move_handle_node, cursor_handle)

    gesture_node.add_next(pre_node)
    pre_node.add_next(cursor_node)

    return CombineFlowNode(gesture_node, cursor_node)


_inited = False


def init_graph():
    global _inited
    if _inited:
        return
    _inited = True
    camera_node.add_next(land_mark_model_node)

    land_mark_model_node.add_next(hands_filter_node)

    hands_filter_node.add_next(cursor_move_handle_node)

    if "is_server" not in config:
        logger.info("no server")
        hands_filter_node.add_next(draw_node)

        draw_node.add_next(show_frame_node)

    for it, handle in gesture_and_cursor_handle_mapping.items():
        hands_filter_node.add_next(gen_gesture_and_cursor_combine_node(it, handle))


def _clear_next_nodes(*nodes: FlowNode):
    for n in nodes:
        n.next_nodes.clear()


def clean_graph():
    global _inited
    if not _inited:
        return
    _inited = False

    _clear_next_nodes(
        camera_node,
        land_mark_model_node,
        hands_filter_node,
        draw_node,
        cursor_move_handle_node,
    )


class FlowManage:
    def __init__(self, start_node: FlowNode[None, Any]) -> None:
        self.start_node = start_node
        self._running = False
        self.task: asyncio.Task | None = None

    def _start(self):
        set_thread_priority_to_high()
        self.start_node.init()
        while self._running:
            run_flow(self.start_node, None)
        self.start_node.clean_effect()
        clean_graph()
        logger.info("flow stop")

    @property
    def running(self):
        return self._running and (self.task is None or not self.task.done())

    async def wait_node_has_value(self, node: FlowNode, max_wait: int = 60):
        t_start = time.time()
        while True:
            if node.output is not NoResult:
                break
            if time.time() - t_start > max_wait:
                raise TimeoutError("wait_node_has_value time out")
            await asyncio.sleep(0.5)

    def start(self, in_async: bool = False):
        init_graph()
        if self.running:
            raise RuntimeError("网络已经在运行")
        self._running = True
        if in_async:
            cor = asyncio.to_thread(self._start)
            self.task = asyncio.create_task(cor)
        else:
            self._start()

    async def stop(self):
        if not self._running or self.task is None or self.task.done():
            raise RuntimeError("flow is not running")
        self._running = False
        await asyncio.wait_for(self.task, 10)

    @property
    def state(self):
        return {"running": self._running}


flow_manager = FlowManage(camera_node)


def start_flow():
    flow_manager.start()
