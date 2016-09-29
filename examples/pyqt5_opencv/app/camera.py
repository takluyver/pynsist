from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QObject
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage
import cv2


class CameraDevice(QObject):

    frame_ready = pyqtSignal(QImage)

    def __init__(self, device_id=0):
        super().__init__()
        self.capture = cv2.VideoCapture(device_id)
        self.timer = QTimer()

        if not self.capture.isOpened():
            raise ValueError("Device not found")

        self.timer.timeout.connect(self.read_frame)
        self.timer.setInterval(1000 / (self.fps or 30))
        self.timer.start()

    def __del__(self):
        self.timer.stop()
        self.capture.release()

    @property
    def fps(self):
        """Frames per second."""
        return int(self.capture.get(cv2.CAP_PROP_FPS))

    @property
    def size(self):
        """Returns the size of the video frames: (width, height)."""
        width = int(self.capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return (width, height)

    def read_frame(self):
        """Read frame into QImage and emit it."""
        success, frame = self.capture.read()
        if success:
            img = _convert_array_to_qimage(frame)
            self.frame_ready.emit(img)
        else:
            raise ValueError("Failed to read frame")


def _convert_array_to_qimage(a):
    height, width, channels = a.shape
    bytes_per_line = channels * width
    cv2.cvtColor(a, cv2.COLOR_BGR2RGB, a)
    return QImage(a.data, width, height, bytes_per_line, QImage.Format_RGB888)
