"""
Code created by both team members in equal distribution
Overall Structure of code for dollar one recognizer taken from
"Gestures without Libraries, Toolkits or Training: A $1 Recognizer
for User Interface Prototypes"
The tested gestures were: line, triangle, circle, square
"""

import sys
import math
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from QDrawWidget import QDrawWidget
from dollar_one_model import Dollar_One_Model


# We create a ControlWindow to handle the visible UI
class ControlWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.initUIComponents()
        self.gestures = {}
        self.is_recognizing = True

    def initUIComponents(self):
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText("Switch between modes by pushing the buttons")
        self.label1.setMinimumSize(900, 100)
        self.label1.move(175, 0)

        self.recognized_gesture = QtWidgets.QLabel(self)
        self.recognized_gesture.setText("Recognized Gesture: ")
        self.recognized_gesture.setMinimumSize(500, 100)
        self.recognized_gesture.move(300, 120)

        self.record_button = QtWidgets.QPushButton(self)
        self.record_button.setText("Record")
        self.record_button.setMinimumSize(150, 50)
        self.record_button.setStyleSheet("background-color :  green")
        self.record_button.move(300, 100)
        self.record_button.clicked.connect(self.record_button_clicked)

        self.gesture_name_line = QtWidgets.QLineEdit(self)
        self.gesture_name_line.setText("")
        self.gesture_name_line.setMinimumSize(400, 20)
        self.gesture_name_line.move(200, 200)

        self.gesture_add_button = QtWidgets.QPushButton(self)
        self.gesture_add_button.setText("add")
        self.gesture_add_button.setMinimumSize(50, 20)
        self.gesture_add_button.move(610, 200)
        self.gesture_add_button.clicked.connect(
            lambda: self.add_gesture(self.gesture_name_line.text().strip()))

        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText("Add to existing gesture type: ")
        self.label3.setMinimumSize(250, 20)
        self.label3.move(200, 240)

        self.gesture_box = QtWidgets.QComboBox(self)
        self.gesture_box.setMinimumSize(150, 20)
        self.gesture_box.move(400, 240)

    # We create a dictionary of gestures
    # keys as the users entered name and values for our list of points
    def add_gesture(self, name):
        if name not in self.gestures and name != "":
            self.gestures[name] = []
            self.gesture_box.clear()
            self.gesture_box.addItems(self.gestures.keys())
            self.gesture_box.setCurrentText(name)
        else:
            sys.stderr.write(
                "A gesture name already exists or is empty. Choose another name")

    # We switch between recording and recognizing
    # Switch when the user pushes one button or another
    def record_button_clicked(self):
        self.gesture_add_button.setEnabled(
            not self.gesture_add_button.isEnabled())
        self.gesture_box.setEnabled(not self.gesture_box.isEnabled())
        if self.is_recognizing:
            self.recognized_gesture.setText("Recording Gesture")
            self.record_button.setText("Stop Recording")
            self.record_button.setStyleSheet("background-color :  red")
        else:
            self.recognized_gesture.setText("Recogized Gesture: ")
            self.record_button.setText("Record")
            self.record_button.setStyleSheet("background-color :  green")
        self.is_recognizing = not self.is_recognizing
        print(self.is_recognizing)


# We create a canvas with a QDrawWidget in a QMainWindow to separate our UI
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.setMinimumSize(800, 800)
        self.dollar_model = Dollar_One_Model()
        self.initUI()

    def initUI(self):
        self.drawing_area = QDrawWidget()
        self.drawing_area.draw.connect(self.dollar_one)
        self.ctrl_window = ControlWindow()
        layout = QtGui.QGridLayout()
        layout.addWidget(self.drawing_area, 1, 0)
        layout.addWidget(self.ctrl_window, 0, 0)
        cw = QtGui.QWidget()
        cw.setLayout(layout)
        self.setCentralWidget(cw)

    # This is the primary function that handles the entire algorithm
    # step 1 - resample , step 2 - rotate , step 3 - scale , step 4 - recognize
    # We take our drawn points on the canvas once
    # process it by passing it to new_points again and again
    # code for the steps itself can be found in dollar_one_model.py
    @QtCore.pyqtSlot()
    def dollar_one(self):
        n = 32
        if n > len(self.drawing_area.points):
            self.ctrl_window.recognized_gesture.setText(
                "Not enough points: either draw slower or a larger shape!")
            return
        new_points = self.dollar_model.resample_points(self.drawing_area.points, n)
        new_points = self.dollar_model.rotate(new_points)
        new_points = self.dollar_model.scale(new_points)
        if self.ctrl_window.is_recognizing:
            print("recognize")
            self.ctrl_window.recognized_gesture.setText(
                "recognized Gesture:" + self.dollar_model.recognize(new_points, self.ctrl_window.gestures))
        else:
            print("record")
            self.ctrl_window.gestures[self.ctrl_window.gesture_box.currentText()] = new_points


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
