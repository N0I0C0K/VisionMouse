import cv2


def show_frame_local(frame: cv2.typing.MatLike) -> bool:
    cv2.imshow("test", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        return False
    return True


def close():
    cv2.destroyAllWindows()
