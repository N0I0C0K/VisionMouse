import asyncio

from fastapi import APIRouter, WebSocket
from fastapi.responses import StreamingResponse
from fastapi.exceptions import WebSocketException

from utils import logger
from controllers.camera import read_real_time_camera, camera, gen_jpeg_content

camera_router = APIRouter(prefix="/camera")


@camera_router.websocket("/test")
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


@camera_router.get("/feed")
async def video_feed():
    return StreamingResponse(
        gen_jpeg_content(), media_type="multipart/x-mixed-replace; boundary=frame"
    )


@camera_router.get("/open")
async def open_camera():
    camera.open()
    return camera.state.to_dict()


@camera_router.get("/state")
async def get_camera_state():
    return camera.state.to_dict()


@camera_router.get("/close")
async def close_camera():
    camera.close()
    return camera.state.to_dict()
