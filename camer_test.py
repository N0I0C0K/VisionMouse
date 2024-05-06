import sys
import time
from queue import Queue

from dataclasses import dataclass, field

import cv2
import numpy as np

# import torch
SYS_PLATFORM = sys.platform

if SYS_PLATFORM.startswith("win32"):
    from pyautogui._pyautogui_win import (
        _moveTo,
        _position,
        _click,
        _mouseDown,
        _mouseUp,
        _vscroll,
    )
elif SYS_PLATFORM.startswith("darwin"):
    from pyautogui._pyautogui_osx import (
        _moveTo,
        _position,
        _click,
        _mouseDown,
        _mouseUp,
        _vscroll,
    )
else:
    raise ImportError


# from model.net import get_model, get_transforms, DEVICE, classes, IMG_SIZE
from mediapipe.python.solutions import hands as mhands
from filter import SlidingWindowMeanFilter


# model = get_model("checkpoints/RetinaNet_ResNet50.pth")
# transform = get_transforms()


# def process_img(img: np.ndarray) -> tuple[tuple[int, int], torch.Tensor]:
#     height, width = img.shape[0], img.shape[1]
#     transformed_image = transform(image=img)
#     processed_image: torch.Tensor = transformed_image["image"] / 255.0

#     return ((width, height), processed_image.to(DEVICE))


Position = tuple[int, int]


def distance(pos1: Position, pos2: Position) -> int:
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


@dataclass
class HandInfo:
    hand_landmark_pos: list[Position]
    camera_size: tuple[int, int]
    c_time: float
    _unit: int = field(init=False)

    def __post_init__(self):
        self._unit = distance(self.hand_landmark_pos[0], self.anchor)

    @property
    def anchor(self) -> Position:
        """
        获取中指根部的坐标，作为整个手掌的锚点
        """
        return self.hand_landmark_pos[9]

    @property
    def unit(self) -> int:
        return self._unit

    @property
    def is_pinch(self) -> bool:
        return self.is_touched(4, 8)

    def is_touched(self, idx1: int, idx2: int) -> bool:
        return self.get_mark_distance(idx1, idx2) * 16 < self.unit

    def get_mark_distance(self, mark_idx1: int, mark_idx2: int) -> int:
        return distance(
            self.hand_landmark_pos[mark_idx1], self.hand_landmark_pos[mark_idx2]
        )

    def anchor_diff(self, other: "HandInfo") -> tuple[Position, float]:
        p = self.anchor
        t = other.anchor
        return (p[0] - t[0], p[1] - t[1]), self.c_time - other.c_time


pos_queue: Queue[HandInfo] = Queue(1)


def raw_model():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    hands = mhands.Hands(
        model_complexity=0,
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.8,
    )

    filters = {4: SlidingWindowMeanFilter(3), 8: SlidingWindowMeanFilter(3)}
    fps_filter: SlidingWindowMeanFilter[float] = SlidingWindowMeanFilter(10)

    while cap.isOpened():
        t1 = time.time()
        ret, frame = cap.read()
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[0], frame.shape[1]
        # (width, height), img = process_img(frame)
        # scale = max(width, height) / IMG_SIZE
        # out = model.forward([img])[0]
        # boxes = out["boxes"][:100]
        # scores = out["scores"][:100]
        # labels = out["labels"][:100]
        # padding_w, padding_h = (
        #     abs(int(IMG_SIZE - width / scale)) // 2,
        #     abs(int(IMG_SIZE - height / scale)) // 2,
        # )
        # for i in range(min(100, len(boxes))):
        #     if scores[i] > 0.7:
        #         print(classes[int(labels[i])], scores[i])
        #         pos1 = int((boxes[i][0] - padding_w) * scale), int(
        #             (boxes[i][1] - padding_h) * scale
        #         )
        #         pos2 = int((boxes[i][2] - padding_w) * scale), int(
        #             (boxes[i][3] - padding_h) * scale
        #         )
        #         cv2.rectangle(frame, pos1, pos2, (0, 255, 0), 2)
        resized_frame = cv2.resize(frame, (width // 2, height // 2))
        results = hands.process(resized_frame[:, :, ::-1])

        if results.multi_hand_landmarks:  # type: ignore
            for hand_landmarks in results.multi_hand_landmarks:  # type: ignore
                hands_info: list[Position] = [(0, 0) for _ in range(22)]
                for idx, landmark in enumerate(hand_landmarks.landmark):
                    x = int(landmark.x * frame.shape[1])
                    y = int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
                    hands_info[idx] = (x, y)
                if not pos_queue.full():
                    pos_queue.put_nowait(
                        HandInfo(hands_info, (width, height), time.time())
                    )
        t2 = time.time()

        dt, _ = fps_filter.push((t2 - t1, 0))
        cv2.putText(
            frame,
            f"{(1/dt):.2f}fps",
            (30, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
        )

        # cv2.imshow("test", frame)
        # key = cv2.waitKey(1) & 0xFF  # 等待按键输入（1毫秒），并取低8位
        # if key == ord("q"):  # 如果按下 'q' 键，退出循环
        #     break

    cap.release()

    # 关闭窗口
    cv2.destroyAllWindows()


def move(dx: int, dy: int) -> Position:
    pos = _position()
    _moveTo(pos[0] + dx, pos[1] + dy)
    return _position()


def direction(dire: tuple[float | int, float | int]) -> tuple[float, float]:
    vec = np.array(dire)
    d_ = vec / max(np.linalg.norm(vec), np.float32(0.0001))
    return d_[0], d_[1]


def mouse_handle():
    from math import sqrt, floor

    last_hand_info = pos_queue.get()
    cur_button_down = False
    pos_filter: SlidingWindowMeanFilter[int] = SlidingWindowMeanFilter(5)
    while True:
        t1 = time.time()
        cur_hand = pos_queue.get()
        (dx, dy), dt = cur_hand.anchor_diff(last_hand_info)
        dt = max(dt, 0.01)
        dx, dy = map(int, pos_filter.push((dx, dy)))
        x_dir, y_dir = direction((dx, dy))
        speed = sqrt(dx**2 + dy**2) / max(dt, 0.001)
        scale = speed / 10 * pow(max(speed, 0.0001), 0.1)

        tx, ty = move(floor(x_dir * scale), floor(y_dir * scale))

        # left mouse control
        if cur_hand.is_pinch and last_hand_info.is_pinch:
            if not cur_button_down:
                _mouseDown(tx, ty, "left")
                cur_button_down = True
        if not cur_hand.is_pinch and not last_hand_info.is_pinch:
            if cur_button_down:
                _mouseUp(tx, ty, "left")
                cur_button_down = False

        # right mouse control
        if cur_hand.is_touched(4, 12) and not last_hand_info.is_touched(4, 12):
            _click(tx, ty, "right")

        # scroll control
        if cur_hand.is_touched(4, 16) and last_hand_info.is_touched(4, 16):
            _vscroll(10, tx, ty)

        # scroll control
        if cur_hand.is_touched(4, 20) and last_hand_info.is_touched(4, 20):
            _vscroll(-10, tx, ty)

        last_hand_info = cur_hand
        t2 = time.time()
        print(f"handler fps:{1/max(t2-t1, 0.001):.2f} {cur_hand.is_pinch = }")


def main():
    from concurrent.futures.thread import ThreadPoolExecutor
    import traceback

    pool = ThreadPoolExecutor(2)
    handler = pool.submit(mouse_handle)
    # camera = pool.submit(raw_model)
    raw_model()
    traceback.print_exception(handler.exception())


main()
