import cv2

class CameraStream:
    def __init__(self, src=0):
        self.cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        self.blink_count = 0

    def read(self):
        if not self.cap.isOpened():
            return None, {"blink_count": self.blink_count}

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None, {"blink_count": self.blink_count}

        return frame, {"blink_count": self.blink_count}

    def release(self):
        if self.cap.isOpened():
            self.cap.release()
