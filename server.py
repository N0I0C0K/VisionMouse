from fastapi import FastAPI

from routes.camera import camera_api
from routes.flow import flow_api
from routes.mouse import mouse_api

from controllers.camera import CameraHelper

from utils import config, logger


on_shutdown = [CameraHelper.close_instance]
config["is_server"] = True


app = FastAPI(on_shutdown=on_shutdown)
app.include_router(camera_api)
app.include_router(flow_api)
app.include_router(mouse_api)

if config["is_dev"]:
    from fastapi.middleware.cors import CORSMiddleware
    from utils.middle_ware import error_handling_middleware

    logger.info("dev mode")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(error_handling_middleware)
