import cv2
import numpy as np
import torch

from queue import Queue

from model.net import get_model, get_transforms, DEVICE, classes, IMG_SIZE

from mediapipe.python.solutions import hands as mhands

from filter import SlidingWindowMeanFilter

import pyautogui

model = get_model("checkpoints/RetinaNet_ResNet50.pth")
transform = get_transforms()


def process_img(img: np.ndarray) -> tuple[tuple[int, int], torch.Tensor]:
    height, width = img.shape[0], img.shape[1]
    transformed_image = transform(image=img)
    processed_image: torch.Tensor = transformed_image["image"] / 255.0

    return ((width, height), processed_image.to(DEVICE))


pos_queue: Queue[tuple[int, int]] = Queue(1)


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
    with torch.no_grad():
        while cap.isOpened():
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
                    for idx, landmark in enumerate(hand_landmarks.landmark):
                        x = int(landmark.x * frame.shape[1])
                        y = int(landmark.y * frame.shape[0])
                        if idx == 8 or idx == 4:  # 食指指尖的关键点索引为8
                            # pos = filters[idx].push((x, y))
                            cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)

                            if idx == 8:
                                pos_queue.put((x, y))

            cv2.imshow("test", frame)
            key = cv2.waitKey(1)

    cap.release()

    # 关闭窗口
    cv2.destroyAllWindows()


def mouse_handle():

    last_pos = pos_queue.get()
    while True:
        # print(pos_queue.qsize())
        pos = pos_queue.get()
        dx = pos[0] - last_pos[0]
        dy = pos[1] - last_pos[1]
        pyautogui.move(dx, dy, duration=0.1)
        last_pos = pos


def main():
    from concurrent.futures.thread import ThreadPoolExecutor

    pool = ThreadPoolExecutor(2)
    handler = pool.submit(mouse_handle)
    raw_model()


main()
