'''
Code created by both team members in equal distribution
Overall Structure of code for dollar one recognizer taken from
"Gestures without Libraries, Toolkits or Training: A $1 Recognizer
for User Interface Prototypes"
'''
import sys
import math
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from QDrawWidget import QDrawWidget


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
        self.gesture_add_button.clicked.connect
        (lambda: self.add_gesture(self.gesture_name_line.text().strip()))

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
            sys.stderr.write
            ("A gesture name already exists or is empty. Choose another name")

    # We switch between recording and recognizing
    # Switch when the user pushes one button or another
    def record_button_clicked(self):
        self.gesture_add_button.setEnabled
        (not self.gesture_add_button.isEnabled())
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
        self.bounding_box_size = 500
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

    # Self-written method which is later used twice within our $1 algorithm
    def calc_distance(self, p1, p2):
        distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return distance

    # This is the primary function that handles the entire algorithm
    # step 1 - resample , step 2 - rotate , step 3 - scale , step 4 - recognize
    # We take our drawn points on the canvas once
    # process it by passing it to new_points again and again
    @QtCore.pyqtSlot()
    def dollar_one(self):
        n = 32
        if n > len(self.drawing_area.points):
            self.ctrl_window.recognized_gesture.setText
            ("Not enough points: either draw slower or a larger shape!")
            return
        new_points = self.resample_points(self.drawing_area.points, n)
        new_points = self.rotate(new_points)
        new_points = self.scale(new_points)
        if self.ctrl_window.is_recognizing:
            print("recognize")
            self.ctrl_window.recognized_gesture.setText
            ("recognized Gesture:" + self.recognize(
                new_points, self.ctrl_window.gestures))
        else:
            print("record")
            self.ctrl_window.gestures
            [self.ctrl_window.gesture_box.currentText()] = new_points

    # step 1 - as discussed in the paper we take n=32 for equally spaced points
    def resample_points(self, points, n):
        stroke_length = 0
        i = 1
        new_points = [points[0]]
        # calculate length of stroke
        while i < len(points):
            p1 = points[i - 1]
            p2 = points[i]
            distance = self.calc_distance(p1, p2)
            stroke_length += distance
            i += 1

        l = stroke_length / (n - 1)
        distance_sum = 0.0
        i = 1
        while i < len(points):
            p1 = points[i - 1]
            p2 = points[i]
            distance = self.calc_distance(p1, p2)
            if distance_sum + distance >= l:
                x = p1[0] + ((l - distance_sum) / distance) * (p2[0] - p1[0])
                y = p1[1] + ((l - distance_sum) / distance) * (p2[1] - p1[1])
                point = (x, y)
                new_points.append(point)
                points.insert(i, point)
                distance_sum = 0
            else:
                distance_sum += distance
            i += 1
        # taken from: http://depts.washington.edu/acelab/proj/dollar/dollar.js
        if len(new_points) == n - 1:
            # sometimes we fall a rounding-error short of adding the last point
            # so add 1 it if so
            new_points.append
            ((points[len(points) - 1][0], points[len(points) - 1][1]))
        return new_points

    # step 2 - decomposed into two methods as suggested in the pseudo-code
    def rotate(self, points):
        new_points = self.rotate_to_zero(points)
        new_points = self.rotate_by
        (new_points, self.indicative_angle(new_points))
        return new_points

    def rotate_to_zero(self, points):
        new_points = self.rotate_by(points, -self.indicative_angle(points))
        return new_points

    def indicative_angle(self, points):
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))
        indicative_angle = np.arctan2
        (centroid[1] - points[0][1], centroid[0] - points[0][0])
        return indicative_angle

    def rotate_by(self, points, angle):
        new_points = []
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))
        for p in points:
            qx = (p[0] - centroid[0]) * np.cos(angle) -
            (p[1] - centroid[1]) * np.sin(angle) + centroid[0]
            qy = (p[0] - centroid[0]) * np.sin(angle) +
            (p[1] - centroid[1]) * np.cos(angle) + centroid[1]
            new_points.append((qx, qy))
        return new_points

    # step 3 - the initial size of the bounding box is set with 500
    def scale(self, points):
        new_points = self.scale_to_square(points, self.bounding_box_size)
        new_points = self.translate_to_origin(new_points)
        return new_points

    def scale_to_square(self, points, size):
        new_points = []
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        min_x, min_y = np.min(x_coordinates), np.min(y_coordinates)
        max_x, max_y = np.max(x_coordinates), np.max(y_coordinates)

        box_width = max_x - min_x
        box_height = max_y - min_y

        for p in points:
            qx = p[0] * (size / box_width)
            qy = p[1] * (size / box_height)
            new_points.append((qx, qy))
        return new_points

    def translate_to_origin(self, points):
        new_points = []
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))

        for p in points:
            qx = p[0] - centroid[0]
            qy = p[1] - centroid[1]
            new_points.append((qx, qy))
        return new_points

    # step 4 - we integrated some error handling
    # for the case that the gesture has not been recorded yet
    # an angle of 45 degrees and a thresold of 2 degrees is
    # suggested in the paper
    def recognize(self, points, gestures):
        b = np.inf
        template_angle = 45  # degrees
        template_thresold = 2
        # if no gestures have been recorded:
        updated_template = " no recorded gestures"
        for template in gestures:
            if gestures[template] == []:
                continue
            d = self.distance_at_best_angle
            (points, gestures[template]
            , template_angle, -template_angle, template_thresold)
            if d < b:
                b = d
                updated_template = template
        score = 1 - (b / 0.5 * np.sqrt(
            self.bounding_box_size ** 2 + self.bounding_box_size ** 2))
        print("template: ", updated_template)
        print("score: ", score)
        return updated_template  # , score

    # The golden ratio calculates an angle
    def distance_at_best_angle
    (self, points, template, angle_a, angle_b, angle_threshold):
        golden_ratio = 0.5 * (-1 + np.sqrt(5))
        x1 = golden_ratio * angle_a + (1 - golden_ratio) * angle_b
        f1 = self.distance_at_angle(points, template, x1)
        x2 = (1 - golden_ratio) * angle_a + golden_ratio * angle_b
        f2 = self.distance_at_angle(points, template, x2)

        while np.abs(angle_b - angle_a) > angle_threshold:
            if f1 < f2:
                angle_b = x2
                x2 = x1
                f2 = f1
                x1 = golden_ratio * angle_a + (1 - golden_ratio) * angle_b
                f1 = self.distance_at_angle(points, template, x1)
            else:
                angle_a = x1
                x1 = x2
                f1 = f2
                x2 = (1 - golden_ratio) * angle_a + golden_ratio * angle_b
                f2 = self.distance_at_angle(points, template, x2)
        return min(f1, f2)

    def distance_at_angle(self, points, template, angle):
        new_points = self.rotate_by(points, angle)
        d = self.path_distance(new_points, template)
        return d

    def path_distance(self, a, b):
        d = 0
        for i in range(len(a)):
            d = d + self.calc_distance(a[i], b[i])
        return d / len(a)


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
