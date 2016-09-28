import os
import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi

from .camera import CameraDevice

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = loadUi(os.path.join(THIS_DIR, 'mainwindow.ui'), self)

        self.thread = QThread()

        try:
            self.camera = CameraDevice()
        except ValueError:
            self.ui.video.setText("Device not found!\n\nIs FFMPEG available?")
        else:
            self.camera.frame_ready.connect(self.update_video_label)
            self.ui.video.setMinimumSize(*self.camera.size)
            self.camera.moveToThread(self.thread)

    @pyqtSlot(QImage)
    def update_video_label(self, image):
        pixmap = QPixmap.fromImage(image)
        self.ui.video.setPixmap(pixmap)
        self.ui.video.update()


def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
