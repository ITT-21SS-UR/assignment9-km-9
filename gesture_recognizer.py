import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QColor, QPainter, QPen
import math
import numpy as np
from QDrawWidget import QDrawWidget


class ControlWindow(QtWidgets.QWidget):
    def __init__(self):
        super(ControlWindow, self).__init__()
        self.setGeometry(700, 100, 800, 500)
        self.initUIComponents()
        self.gestures = {}
        self.is_recognizing = True

    def initUIComponents(self):
        self.label1 = QtWidgets.QLabel(self)
        self.label1.setText("Switch between record and recognition mode by pushing the buttons")
        self.label1.setMinimumSize(900, 100)
        self.label1.move(175, 0)

        self.recognized_gesture = QtWidgets.QLabel(self)
        self.recognized_gesture.setText("Recognized Gesture: ")
        self.recognized_gesture.setMinimumSize(500, 100)
        self.recognized_gesture.move(300, 120)

        self.record_button = QtWidgets.QPushButton(self)
        self.record_button.setText("Record")
        self.record_button.setMinimumSize(150, 50)
        self.record_button.setStyleSheet("background-color :  blue")
        self.record_button.move(200, 100)
        self.record_button.clicked.connect(self.record_button_clicked)

        self.recognize_button = QtWidgets.QPushButton(self)
        self.recognize_button.setText("Recognize")
        self.recognize_button.setMinimumSize(150, 50)
        self.recognize_button.setStyleSheet("background-color : yellow")
        self.recognize_button.move(400, 100)
        self.recognize_button.clicked.connect(self.recognize_button_clicked)

        self.gesture_name_line = QtWidgets.QLineEdit(self)
        self.gesture_name_line.setText("")
        self.gesture_name_line.setMinimumSize(400, 20)
        self.gesture_name_line.move(200, 200)

        self.gesture_add_button = QtWidgets.QPushButton(self)
        self.gesture_add_button.setText("add")
        self.gesture_add_button.setMinimumSize(50, 20)
        self.gesture_add_button.move(610, 200)
        self.gesture_add_button.clicked.connect(lambda: self.add_gesture(self.gesture_name_line.text().strip()))

        self.label3 = QtWidgets.QLabel(self)
        self.label3.setText("Add to existing gesture type: ")
        self.label3.setMinimumSize(250, 20)
        self.label3.move(200, 240)

        self.gesture_box = QtWidgets.QComboBox(self)
        self.gesture_box.setMinimumSize(150, 20)
        self.gesture_box.move(400, 240)

    def add_gesture(self, name):
        if name not in self.gestures and name != "":
            self.gestures[name] = []
            self.gesture_box.clear()
            self.gesture_box.addItems(self.gestures.keys())
        else:
            sys.stderr.write("The gesture name either already exists or is empty. Please choose another name")

    def record_button_clicked(self):
        self.gesture_add_button.setEnabled(False)
        self.gesture_box.setEnabled(False)
        self.label1.setText("Recognized Gesture: ")
        self.is_recognizing = False
    #     print("record active!")

    def recognize_button_clicked(self):
        self.gesture_add_button.setEnabled(True)
        self.gesture_box.setEnabled(True)
        self.label1.setText("Recognized Gesture: ")
        self.is_recognizing = True


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

    def calc_distance(self, p1, p2):
        distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return distance

    @QtCore.pyqtSlot()
    def dollar_one(self):
        n = 32
        if n > len(self.drawing_area.points):
            self.ctrl_window.recognized_gesture.setText("Not enough points: either draw slower or a larger shape!")
            return
        new_points = self.resample_points(self.drawing_area.points, n)
        new_points = self.rotate(new_points)
        new_points = self.scale(new_points)
        print(new_points)
        # new_points = self.recognize(new_points)
        if self.ctrl_window.is_recognizing:
            print("recognize")
            self.ctrl_window.recognized_gesture.setText(self.recognize(new_points, self.ctrl_window.gestures))
        else:
            print("record")
            self.ctrl_window.gestures[self.ctrl_window.gesture_box.currentText()].append(new_points)

        # new_points = self.scale((self.rotate(self.resample_points(points))))

    def resample_points(self, points, n):
        stroke_length = 0
        i = 1
        new_points = []
        if len(points) < 32:
            print("not enough points")

        else:
            # calculate length of stroke
            while i < len(points):
                p1 = points[i-1]
                p2 = points[i]
                distance = self.calc_distance(p1, p2)
                stroke_length += distance
                i += 1

            l = stroke_length / (n - 1)
            print("l", l)
            distance_sum = 0.0
            i = 1
            # resample points to n evenly spaced points
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

            # print(new_points)
            return new_points

    def rotate(self, points):
        new_points = self.rotate_to_zero(points)
        new_points = self.rotate_by(new_points, self.indicative_angle(new_points))
        return new_points

    def indicative_angle(self, points):
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))
        indicative_angle = np.arctan2(centroid[1] - points[0][1], centroid[0] - points[0][0])
        return indicative_angle

    def rotate_to_zero(self, points):
        new_points = self.rotate_by(points, -self.indicative_angle(points))
        return new_points


    def rotate_by(self, points, angle):
        new_points = []
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))
        for p in points:
            qx = (p[0] - centroid[0]) * np.cos(angle) - (p[1] - centroid[1]) * np.sin(angle) + centroid[0]
            qy = (p[0] - centroid[0]) * np.sin(angle) + (p[1] - centroid[1]) * np.cos(angle) + centroid[1]
            new_points.append((qx, qy))
        return new_points

    def scale(self, points):
        new_points = self.scale_to_square(points, 500)
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

    def recognize(self, points, gestures):
        b = np.inf
        print("B", b)
        template_angle = 45  # grad
        template_thresold = 2
        for template in gestures:
            d = self.distance_at_best_angle(points, template, template_angle, -template_angle, template_thresold)
            print("d",d)
            if d < b:
                b = d
                updated_template = template
        score = 1 - (b / 0.5 * np.sqrt(self.bounding_box_size ** 2 + self.bounding_box_size ** 2))
        return updated_template, score

    def distance_at_best_angle(self, points, gestures, angle_a, angle_b, angle_threshold):
        golden_ratio = 0.5 * (-1 + np.sqrt(5))
        x1 = golden_ratio * angle_a + (1 - golden_ratio) * angle_b
        f1 = self.distance_at_angle(points, gestures, x1)
        x2 = (1 - golden_ratio) * angle_a + golden_ratio * angle_b
        f2 = self.distance_at_angle(points, gestures, x2)

        while np.abs(angle_b - angle_a) > angle_threshold:
            if f1 < f2:
                angle_b = x2
                x2 = x1
                f2 = f1
                x1 = golden_ratio * angle_a + (1 - golden_ratio) * angle_b
                f1 = self.distance_at_angle(points, gestures, x1)
            else:
                angle_a = x1
                x1 = x2
                f1 = f2
                x2 = (1 - golden_ratio) * angle_a + golden_ratio * angle_b
                f2 = self.distance_at_angle(points, gestures, x2)
        return np.min(f1,f2)

    def distance_at_angle(self, points, gestures, angle):
            new_points = self.rotate_by(points, angle)
            d = self.path_distance(new_points, gestures)
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
