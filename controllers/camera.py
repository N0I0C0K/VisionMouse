import cv2
from typing import NamedTuple, Iterable
from typing_extensions import Self


class FrameTuple(NamedTuple):
    frame: cv2.typing.MatLike
    width: int
    height: int


class SizeTuple(NamedTuple):
    width: int
    height: int

    def to_dict(self):
        return {"width": self.width, "height": self.height}


class CameraState(NamedTuple):
    is_opened: bool
    size: SizeTuple

    def to_dict(self):
        return {"isOpened": self.is_opened, "size": self.size.to_dict()}


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
        return CameraState(self.is_opened, self.size)

    def open(self):
        if self.is_opened:
            return
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.size.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.size.height)

    def close(self):
        if not self.is_opened:
            raise RuntimeError("cap is not opened")
        self.cap.release()  # type: ignore

    def __init__(self):
        self.cap: cv2.VideoCapture | None = None
        self.size = SizeTuple(1280, 720)

    def read(self):
        if not self.is_opened:
            raise RuntimeError("cap is not opened")
        ret, frame = self.cap.read()  # type: ignore
        if not ret:
            raise RuntimeError("read camera failed")
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[0], frame.shape[1]
        self.size = SizeTuple(width, height)
        return FrameTuple(frame, width, height)

    @classmethod
    def get_instance(cls) -> Self:
        if cls._global_camer is None:
            cls._global_camer = cls()
        return cls._global_camer

    @classmethod
    def close_instance(cls):
        if cls._global_camer:
            cls._global_camer.close()


camera = CameraHelper.get_instance()


def read_real_time_camera() -> Iterable[FrameTuple]:
    while True:
        yield camera.read()


def read_real_time_camera_to_jpeg() -> Iterable[bytes]:
    for frame in read_real_time_camera():
        ret, jpeg = cv2.imencode(".jpeg", frame.frame)
        if not ret:
            raise RuntimeError("convert raw video to jpg failed")
        yield jpeg.tobytes()


def gen_jpeg_content() -> Iterable[bytes]:
    for jpeg in read_real_time_camera_to_jpeg():
        yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n")
