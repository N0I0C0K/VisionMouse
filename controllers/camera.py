import cv2
import time

from typing import Iterable
from typing_extensions import Self

from utils import logger
from controllers.types import CameraSettingModel, CameraState, SizeTuple, FrameTuple


class CameraHelper:
    _global_camer: Self | None = None

    def __new__(cls, *args, **kwargs) -> Self:
        if cls._global_camer:
            raise RuntimeError("please use get_instance")
        obj = super().__new__(cls)
        cls._global_camer = obj
        return obj

    @property
    def is_opened(self) -> bool:
        return self.cap is not None and self.cap.isOpened()

    @property
    def state(self) -> CameraState:
        return CameraState(self.is_opened, self.size, self.exposure)

    def open(self):
        if self.is_opened:
            return
        logger.info("start open camera")
        cap = self.cap
        cap.open(0)
        cap_index, cap_name = cap.get(cv2.CAP_PROP_POS_MSEC), cap.get(
            cv2.CAP_PROP_POS_FRAMES
        )
        logger.info(f"{cap_index = }, {cap_name = }")
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G"))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.size.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size.height)
        cap.set(cv2.CAP_PROP_EXPOSURE, self.exposure)
        cap.set(cv2.CAP_PROP_FPS, 30)

        logger.info("open camera complete")

    def close(self):
        if not self.is_opened:
            logger.warning("cap is not opening, but want to close")
            return
        self.cap.release()  # type: ignore

    def __init__(self):
        self.cap: cv2.VideoCapture = cv2.VideoCapture()
        self.size = SizeTuple(1280, 720)
        self.exposure = -5

    def read(self, auto_open: bool = False):
        if not self.is_opened:
            if auto_open:
                self.open()
            else:
                raise RuntimeError("cap is not opened")
        ret, frame = self.cap.read()  # type: ignore
        if not ret:
            raise RuntimeError("read camera failed")
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[0], frame.shape[1]
        self.size = SizeTuple(width, height)
        return FrameTuple(frame, width, height, time.time())

    @classmethod
    def get_instance(cls) -> Self:
        if cls._global_camer is None:
            cls._global_camer = cls()
        return cls._global_camer

    @classmethod
    def close_instance(cls):
        if cls._global_camer:
            cls._global_camer.close()

    def update_camera_setting(self, setting: CameraSettingModel):
        if self.cap is None:
            raise RuntimeError("please init camera first")
        if setting.exposure is not None:
            self.cap.set(cv2.CAP_PROP_EXPOSURE, setting.exposure)
            self.exposure = setting.exposure

    def __del__(self):
        self.close()


camera = CameraHelper.get_instance()


def read_real_time_camera() -> Iterable[FrameTuple]:
    while True:
        yield camera.read()


def read_real_time_camera_to_jpeg(
    frame_gen: Iterable[cv2.typing.MatLike],
) -> Iterable[bytes]:
    for frame in frame_gen:
        ret, jpeg = cv2.imencode(".jpeg", frame)
        if not ret:
            raise RuntimeError("convert raw video to jpg failed")
        yield jpeg.tobytes()


def gen_jpeg_content() -> Iterable[bytes]:
    for jpeg in read_real_time_camera_to_jpeg(
        map(lambda x: x.frame, read_real_time_camera())
    ):
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
