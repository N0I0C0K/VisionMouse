import time

import mediapipe as mp

from mediapipe.tasks.python.core.base_options import BaseOptions
from mediapipe.tasks.python.vision.core.vision_task_running_mode import (
    VisionTaskRunningMode,
)
from mediapipe.tasks.python.vision.hand_landmarker import (
    HandLandmarker,
    HandLandmarkerOptions,
)


from controllers.types import FrameTuple
from controllers.hand_info import HandInfo

model_path = "./controllers/model/hand_landmarker.task"


class HandLandMarkModelV2:
    def __init__(self) -> None:
        with open(model_path, "rb") as file:
            buffer = file.read()
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_buffer=buffer),
            running_mode=VisionTaskRunningMode.VIDEO,
            num_hands=2,
            min_hand_detection_confidence=0.7,
        )
        self.landmarker = HandLandmarker.create_from_options(options)

    def forward(self, frame: FrameTuple) -> list[HandInfo]:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame.frame)
        hand_land_mark_result = self.landmarker.detect_for_video(
            mp_image, int(frame.ctime * 1000)
        )
        res: list[HandInfo] = []
        width, height = frame.width, frame.height
        for hand_pos in hand_land_mark_result.hand_landmarks:
            land_pos = [
                (float(pos.x * width), float(pos.y * height)) for pos in hand_pos
            ]
            res.append(HandInfo(land_pos, (width, height), time.time()))
        return res

    def close(self):
        self.landmarker.close()
