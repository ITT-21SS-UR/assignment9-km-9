import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QPainter, QPen

from QDrawWidget import QDrawWidget

class ControlWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.initUIComponents()

    def initUIComponents(self):
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText("Switch between record and recognition mode by pushing the buttons")
        self.label1.setMinimumSize(900, 100)
        self.label1.move(175,0)


        record_button = QtWidgets.QPushButton(self)
        record_button.setText("Record")
        record_button.setMinimumSize(150,50)
        record_button.setStyleSheet("background-color :  blue")
        record_button.move(200, 100)
        record_button.clicked.connect(self.record_button_clicked)

        recognize_button = QtWidgets.QPushButton(self)
        recognize_button.setText("Recognize")
        recognize_button.setMinimumSize(150,50)
        recognize_button.setStyleSheet("background-color : yellow")
        recognize_button.move(400, 100)
        recognize_button.clicked.connect(self.recognize_button_clicked)

        gesture_name_line = QtWidgets.QLineEdit(self)
        gesture_name_line.setText("")
        gesture_name_line.setMinimumSize(400,20)
        gesture_name_line.move(200,200)

        gesture_save_button = QtWidgets.QPushButton(self)
        gesture_save_button.setText("save")
        gesture_save_button.setMinimumSize(50,20)
        gesture_save_button.move(610,200)

    def record_button_clicked(self):
            print("record active!")

    def recognize_button_clicked(self):
            print("recognition active!")


class GestureWindow(QMainWindow):
    def __init__(self):
        super(GestureWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.initUI()

    def initUI(self):
        self.drawing_area = QDrawWidget()
        self.ctrl_window = ControlWindow()
        layout = QtGui.QGridLayout()
        layout.addWidget(self.drawing_area, 1, 0)
        layout.addWidget( self.ctrl_window, 0, 0)
        cw = QtGui.QWidget()
        cw.setLayout(layout)
        self.setCentralWidget(cw)


def main():
    app = QApplication(sys.argv)
    win = GestureWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()