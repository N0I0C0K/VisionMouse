import cv2


def show_frame_local(frame: cv2.typing.MatLike) -> bool:
    cv2.imshow("test", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return False
    return True


def close():
    cv2.destroyAllWindows()


def draw_circle(frame: cv2.typing.MatLike, x: int, y: int):
    cv2.circle(frame, (x, y), 5, (0, 255, 0), -1)
