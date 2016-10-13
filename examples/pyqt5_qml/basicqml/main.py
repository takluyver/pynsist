import os
import sys
import time
import threading
from PyQt5 import QtCore, QtGui, QtQml


THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class JSManager(QtCore.QObject):
    text = QtCore.pyqtSignal(QtCore.QVariant)

    @QtCore.pyqtSlot()
    def get_text(self):
        def go():
            _text = "Hello from JavaScript"
            self.text.emit(_text)
        threading.Thread(target=go).start()


def main():
    app = QtGui.QGuiApplication(sys.argv)
    QtQml.qmlRegisterType(JSManager, 'JSManager', 1, 0, 'JSManager')
    engine = QtQml.QQmlApplicationEngine(os.path.join(THIS_DIR, "main.qml"))
    app.exec_()
