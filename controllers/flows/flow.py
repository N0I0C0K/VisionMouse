import asyncio
import time
from typing import Any

from controllers.flows.node import (
    CameraNode,
    CursorMoveHandleNode,
    FlowNode,
    LandMarkFilterNode,
    GestureRecognizeNode,
    ShowFrameNode,
    DrawLandMarkNode,
    LandMarkV2Node,
    run_flow,
    NoResult,
)
from controllers.flows.control_flow import gen_all_cursor_control_node


from utils import config, logger
from utils.threading import set_thread_priority_to_high


camera_node = CameraNode()

land_mark_model_node = GestureRecognizeNode()
hands_filter_node = LandMarkFilterNode()
cursor_move_handle_node = CursorMoveHandleNode()
show_frame_node = ShowFrameNode()
draw_node = DrawLandMarkNode(camera_node)


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
        camera_node.add_next(show_frame_node)
        # draw_node.add_next(show_frame_node)

    for control_node in gen_all_cursor_control_node():
        hands_filter_node.add_next(control_node)


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
        logger.info("flow start")
        init_graph()
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
