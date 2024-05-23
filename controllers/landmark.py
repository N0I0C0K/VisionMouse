import time
import cv2

from mediapipe.python.solutions import hands as mhands

from controllers.models import HandInfo
from controllers.types import Position, FrameTuple


class HandLandMarkModel:
    def __init__(self) -> None:
        self.hands = mhands.Hands(
            model_complexity=0,
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.8,
        )

    def forward(self, frame_tuple: FrameTuple) -> list[HandInfo]:
        frame, width, height = frame_tuple
        results = self.hands.process(frame[:, :, ::-1])
        hand_info_list: list[HandInfo] = []
        if results.multi_hand_landmarks:  # type: ignore
            for hand_landmarks in results.multi_hand_landmarks:  # type: ignore
                hands_info: list[Position] = [(0, 0) for _ in range(22)]
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    hands_info[idx] = (x, y)
                hand_info_list.append(
                    HandInfo(hands_info, (width, height), time.time())
                )
        return hand_info_list
