import cv2
from typing import NamedTuple, Iterable
from typing_extensions import Self


class FrameTuple(NamedTuple):
    frame: cv2.typing.MatLike
    width: int
    height: int


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

    def open(self):
        if self.is_opened:
            return
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def close(self):
        if not self.is_opened:
            raise RuntimeError("cap is not opened")
        self.cap.release()  # type: ignore

    def __init__(self):
        self.cap: cv2.VideoCapture | None = None

    def __enter__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cap:
            self.cap.release()

    def read(self):
        if not self.is_opened:
            raise RuntimeError("cap is not opened")
        ret, frame = self.cap.read()  # type: ignore
        if not ret:
            raise RuntimeError("read camera failed")
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[0], frame.shape[1]
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
