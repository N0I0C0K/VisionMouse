import asyncio
from typing import cast, Any

from fastapi import APIRouter, WebSocket
from fastapi.websockets import WebSocketState

from controllers.flows.flow import (
    flow_manager,
    camera_node,
    draw_node,
    land_mark_model_node,
    hands_filter_node,
)
from controllers.hand_info import HandInfo
from controllers.flows.node import NoResult

from utils import logger

flow_api = APIRouter(prefix="/flow")


@flow_api.get("/state")
async def get_flow_state():
    return flow_manager.state


@flow_api.get("/start")
async def start_flow():
    flow_manager.start(True)
    await flow_manager.wait_node_has_value(camera_node)
    return flow_manager.state


@flow_api.get("/stop")
async def stop_flow():
    await flow_manager.stop()
    return flow_manager.state


@flow_api.websocket("/landMark/feed")
async def gen_land_mark_sample(ws: WebSocket):
    await ws.accept()
    wait_time = 0
    while ws.client_state == WebSocketState.CONNECTED:
        if wait_time >= 2:
            await ws.receive()
        if not flow_manager.running:
            print("not running")
            await asyncio.sleep(0.5)
            wait_time += 0.5
        try:
            res: dict[str, Any] = {"width": 1280, "height": 720}
            if land_mark_model_node.output is not NoResult:
                hand_info_list = cast(list[HandInfo], land_mark_model_node.output)
                pos_str = "|".join(map(lambda x: x.encode_pos(), hand_info_list))
                if pos_str != "":
                    res["allHand"] = pos_str

            if hands_filter_node.output is not NoResult:
                current_hand = cast(HandInfo, hands_filter_node.output)
                res["currentHand"] = current_hand.encode_pos()
                res["width"] = current_hand.camera_size[0]
                res["height"] = current_hand.camera_size[1]

            if len(res) > 2:
                await ws.send_json(res)
            await asyncio.sleep(0.03)
        except:
            break
    logger.info("land mark close")
    await ws.close()
