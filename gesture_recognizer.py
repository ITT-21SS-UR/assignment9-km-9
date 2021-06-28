import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QPainter, QPen
import math
from QDrawWidget import QDrawWidget


class ControlWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.initUIComponents()
        self.gestures = {}

    def initUIComponents(self):
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText("Switch between record and recognition mode by pushing the buttons")
        self.label1.setMinimumSize(900, 100)
        self.label1.move(175,0)
        self.recognized_gesture = QtWidgets.QLabel(self)
        self.recognized_gesture.setText("Recognized Gesture: ")
        self.recognized_gesture.setMinimumSize(500, 100)
        self.recognized_gesture.move(300, 120)



        self.record_button = QtWidgets.QPushButton(self)
        self.record_button.setText("Record")
        self.record_button.setMinimumSize(150,50)
        self.record_button.setStyleSheet("background-color :  blue")
        self.record_button.move(200, 100)
        self.record_button.clicked.connect(self.record_button_clicked)

        self.recognize_button = QtWidgets.QPushButton(self)
        self.recognize_button.setText("Recognize")
        self.recognize_button.setMinimumSize(150,50)
        self.recognize_button.setStyleSheet("background-color : yellow")
        self.recognize_button.move(400, 100)
        self.recognize_button.clicked.connect(self.recognize_button_clicked)

        self.gesture_name_line = QtWidgets.QLineEdit(self)
        self.gesture_name_line.setText("")
        self.gesture_name_line.setMinimumSize(400,20)
        self.gesture_name_line.move(200,200)
        
        
        self.gesture_add_button = QtWidgets.QPushButton(self)
        self.gesture_add_button.setText("add")
        self.gesture_add_button.setMinimumSize(50,20)
        self.gesture_add_button.move(610,200)
        self.gesture_add_button.clicked.connect(self.add_gesture_to_box)

        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText("Add to existing gesture type: ")
        self.label3.setMinimumSize(250,20)
        self.label3.move(200,240)

        self.gesture_box = QtWidgets.QComboBox(self)
        self.gesture_box.setMinimumSize(150,20)
        self.gesture_box.move(400,240)
        
    def add_gesture_to_box(self):
        self.gestures[self.gesture_name_line.text()] = []
        self.gesture_box.addItems(self.gestures.keys())
        self.gesture_name_line.setText("")
        
    def record_button_clicked(self):
        self.gesture_add_button.setEnabled(False)
        self.gesture_box.setEnabled(False)
        self.label1.setText("Recognized Gesture: ")
        print("record active!")


    def recognize_button_clicked(self):
            print("recognition active!")






class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.setMinimumSize(800,800)
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

    @QtCore.pyqtSlot()
    def dollar_one(self):
        points = self.drawing_area.points
        new_points = self.scale(self.rotate(self.resample_points(points)))

    def resample_points(self, points):
        print(points)
        n = 32
        stroke_length = 0
        i = 1
        new_points = []
        if len(points) < 32:
            print("not enough points")
        # calculate length of stroke
        else:
            while i < len(points):
                # a²+b² = c²
                distance = math.sqrt((points[i][0] - points[i - 1][0]) ** 2 + (points[i][1] - points[i - 1][1]) ** 2)
                stroke_length += distance
                i += 1

            l = stroke_length / (n - 1)
            print(l)
            distance_sum = 0
            i = 1

            # resample points to n evenly spaced points
            while i < len(points):
                distance = math.sqrt((points[i][0] - points[i - 1][0]) ** 2 + (points[i][1] - points[i - 1][1]) ** 2)
                distance_sum += distance
                if distance_sum >= l:
                    x = points[i - 1][0] + ((l - distance_sum) / distance) * (points[i - 1][0] - points[i - 1][0])
                    y = points[i - 1][1] + ((l - distance_sum) / distance) * (points[i - 1][1] - points[i - 1][1])
                    point = (x, y)
                    new_points.append(point)
                    points[i] = point
                    distance_sum = 0
                i += 1
            print(new_points)
            return new_points

    def rotate(self,points):
        #insert step 2
        new_points = []
        return new_points

    def scale(self,points):
        # insert step 3
        new_points = []
        return new_points

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
