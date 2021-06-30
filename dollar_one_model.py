import numpy as np
import math

class Dollar_One_Model():

    def __init__(self):
        self.bounding_box_size = 500

    # method used for calculating distance between two 2D points
    def calc_distance(self, p1, p2):
        distance = math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
        return distance

    # step 1 resample the given points to n evenly spaced points
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
            new_points.append(
                (points[len(points) - 1][0], points[len(points) - 1][1]))
        return new_points

    # step 2 - decomposed into two methods as suggested in the pseudo-code
    def rotate(self, points):
        new_points = self.rotate_to_zero(points)
        new_points = self.rotate_by(
            new_points, self.indicative_angle(new_points))
        return new_points

    def rotate_to_zero(self, points):
        new_points = self.rotate_by(points, -self.indicative_angle(points))
        return new_points

    def indicative_angle(self, points):
        x_coordinates = [p[0] for p in points]
        y_coordinates = [p[1] for p in points]
        centroid = (np.mean(x_coordinates), np.mean(y_coordinates))
        indicative_angle = np.arctan2(
            centroid[1] - points[0][1], centroid[0] - points[0][0])
        return indicative_angle

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
            d = self.distance_at_best_angle(
                points, gestures[template], template_angle, -template_angle, template_thresold)
            if d < b:
                b = d
                updated_template = template
        score = 1 - (b / 0.5 * np.sqrt(
            self.bounding_box_size ** 2 + self.bounding_box_size ** 2))
        print("template: ", updated_template)
        print("score: ", score)
        return updated_template  # , score

    # The golden ratio calculates an angle
    def distance_at_best_angle(self, points, template, angle_a, angle_b, angle_threshold):
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
