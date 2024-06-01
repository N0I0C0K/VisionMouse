import asyncio

from fastapi import APIRouter, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.exceptions import WebSocketException

from controllers.types import CameraSettingModel
from utils import logger, convert_named_tuple_to_dict
from controllers.camera import (
    read_real_time_camera,
    camera,
    gen_jpeg_content,
)
from controllers.flows.flow import flow_manager

camera_api = APIRouter(prefix="/camera")


@camera_api.websocket("/test")
async def test_camera(websockt: WebSocket):
    await websockt.accept()
    try:
        for frame in read_real_time_camera():
            await websockt.send_bytes(frame.frame.tobytes())
            await asyncio.sleep(0.01)
    except WebSocketException as err:
        logger.exception(err)
    finally:
        await websockt.close()


@camera_api.get("/feed")
def video_feed():
    if flow_manager.running:
        raise RuntimeError
    return StreamingResponse(
        gen_jpeg_content(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@camera_api.get("/open")
def open_camera():
    camera.open()
    return convert_named_tuple_to_dict(camera.state, camelCase=True)


@camera_api.get("/state")
async def get_camera_state():
    return convert_named_tuple_to_dict(camera.state, camelCase=True)


@camera_api.get("/close")
async def close_camera():
    camera.close()
    return convert_named_tuple_to_dict(camera.state, camelCase=True)


@camera_api.put("/setting")
async def update_camera_setting(setting: CameraSettingModel):
    camera.update_camera_setting(setting)
    return convert_named_tuple_to_dict(camera.state, camelCase=True)
