import cv2
import numpy as np
import torch
import pyautogui
import time
import typing


from pyautogui._pyautogui_win import (
    _moveTo,
    _position,
    _click,
    _mouseDown,
    _mouseUp,
    _mouse_is_swapped,
)
from queue import Queue
from model.net import get_model, get_transforms, DEVICE, classes, IMG_SIZE
from mediapipe.python.solutions import hands as mhands
from filter import SlidingWindowMeanFilter


model = get_model("checkpoints/RetinaNet_ResNet50.pth")
transform = get_transforms()


def process_img(img: np.ndarray) -> tuple[tuple[int, int], torch.Tensor]:
    height, width = img.shape[0], img.shape[1]
    transformed_image = transform(image=img)
    processed_image: torch.Tensor = transformed_image["image"] / 255.0

    return ((width, height), processed_image.to(DEVICE))


Position = tuple[int, int]


def distance(pos1: Position, pos2: Position) -> int:
    return (pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2


class HandInfo(typing.NamedTuple):
    hand_landmark_pos: list[Position]
    camera_size: tuple[int, int]
    c_time: float

    @property
    def anchor(self) -> Position:
        """
        获取中指根部的坐标，作为整个手掌的锚点
        """
        return self.hand_landmark_pos[9]

    @property
    def unit(self) -> int:
        return distance(self.hand_landmark_pos[0], self.anchor)

    @property
    def is_pinch(self) -> bool:
        return self.get_mark_distance(4, 8) * 16 < self.unit

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
    last_pos = (0, 0)
    fps_filter: SlidingWindowMeanFilter[float] = SlidingWindowMeanFilter(10)
    with torch.no_grad():
        while cap.isOpened():
            t1 = time.time()
            ret, frame = cap.read()
            frame = cv2.flip(frame, 1)
            (width, height), img = process_img(frame)
            scale = max(width, height) / IMG_SIZE
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
                        # if idx == 8 or idx == 4 or idx == 9:  # 食指指尖的关键点索引为8
                        # pos = filters[idx].push((x, y))
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
            # key = cv2.waitKey(1)

    cap.release()

    # 关闭窗口
    cv2.destroyAllWindows()


def move(dx: int, dy: int) -> Position:
    pos = _position()
    _moveTo(pos[0] + dx, pos[1] + dy)
    return _position()


def direction(x: int):
    return 1 if x >= 0 else -1


def mouse_handle():
    last_hand_info = pos_queue.get()

    while True:
        t1 = time.time()
        cur_hand = pos_queue.get()
        (dx, dy), dt = cur_hand.anchor_diff(last_hand_info)
        x_dir, y_dir = direction(dx), direction(dy)
        # scale = (dx**2 + dy**2) / cur_hand.unit * 1000
        tx, ty = move(dx, dy)
        last_hand_info = cur_hand

        if cur_hand.is_pinch:
            _mouseDown(tx, ty, "left")
        else:
            _mouseUp(tx, ty, "left")

        t2 = time.time()
        print(
            f"handler fps:{1/(t2-t1):.2f}, {cur_hand.unit = }, dis:{(dx**2 + dy**2)}, 4-8 dis:{cur_hand.get_mark_distance(4,8)}, click:{cur_hand.is_pinch}"
        )


def main():
    from concurrent.futures.thread import ThreadPoolExecutor

    pool = ThreadPoolExecutor(2)
    handler = pool.submit(mouse_handle)
    raw_model()


main()
