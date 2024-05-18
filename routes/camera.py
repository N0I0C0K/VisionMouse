import asyncio

from fastapi import APIRouter, WebSocket
from fastapi.exceptions import WebSocketException

from utils import logger
from controllers.camera import read_real_time_camera, camera

camera_router = APIRouter(prefix="/camera")


@camera_router.websocket("/test")
async def test_camera(websockt: WebSocket):
    try:
        for frame in read_real_time_camera():
            await websockt.send_bytes(frame.frame.tobytes())
            await asyncio.sleep(0.01)
    except WebSocketException as err:
        logger.exception(err)


@camera_router.get("/open")
async def open_camera():
    camera.open()


@camera_router.get("/state")
async def get_camera_state():
    return {"isOpened": camera.is_opened}


@camera_router.get("/close")
async def close_camera():
    camera.close()
