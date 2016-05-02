import sys
from PyQt4 import QtGui

from .main import Ui_MainWindow

class Main(QtGui.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.add_button.clicked.connect(self.add_item)

    def get_radio_option(self):
        if self.ui.radio_1.isChecked():
            return 'Thing 1'
        elif self.ui.radio_2.isChecked():
            return 'Thing 2'
        elif self.ui.radio_3.isChecked():
            return 'Thing 3'
        elif self.ui.radio_4.isChecked():
            return 'Last thing'
        return 'No thing'
        
    def add_item(self):
        text = self.get_radio_option()
        QtGui.QListWidgetItem(text, self.ui.listWidget)        

def main():
    app = QtGui.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())