from fastapi import FastAPI

from routes.camera import camera_router
from controllers.camera import CameraHelper

on_shutdown = [CameraHelper.close_instance]

app = FastAPI(on_shutdown=on_shutdown)
app.include_router(camera_router)
