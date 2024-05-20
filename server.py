from fastapi import FastAPI

from routes.camera import camera_router
from controllers.camera import CameraHelper

from utils import config, logger


on_shutdown = [CameraHelper.close_instance]

app = FastAPI(on_shutdown=on_shutdown)
app.include_router(camera_router)

if config["is_dev"]:
    from fastapi.middleware.cors import CORSMiddleware

    logger.info("dev mode")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
