import math


class SinglePuzzle:

    def __init__(self):
        self.traces = []
        self.crop_image = None
        self.right_tab = None
        self.left_tab = None
        self.top_tab = None
        self.down_tab = None
        self.threshold = 0

    def __str__(self):
        return "SinglePuzzle{ top_tab=" + str(self.top_tab) + ", down_tab=" + str(self.down_tab) + ", left_tab=" + str(
            self.left_tab) + ", right_tab=" + str(self.right_tab) + "}"

    def define_puzzle_tabs(self):
        down_or_right = False
        down_or_left = False
        top_or_left = False
        top_or_right = False
        for trace in self.traces:
            degree, distance_between_poitns = trace.define_slope_angle_and_distance(threshold=self.threshold)

            if distance_between_poitns > self.threshold:
                if 10 < degree % 90 < 80:
                    if 0 < degree < 90:
                        down_or_right = True
                    if 90 < degree < 180:
                        top_or_right = True
                    if 180 < degree < 270:
                        top_or_left = True
                    if 270 < degree < 360:
                        down_or_left = True
                else:
                    concaveResponse = trace.is_on_start_and_end_line(threshold=self.threshold)
                    if concaveResponse == "straight_down":
                        if self.down_tab is None:
                            self.down_tab = "straight"
                    elif concaveResponse == "straight_top":
                        if self.top_tab is None:
                            self.top_tab = "straight"
                    elif concaveResponse == "straight_right":
                        if self.right_tab is None:
                            self.right_tab = "straight"
                    elif concaveResponse == "straight_left":
                        if self.left_tab is None:
                            self.left_tab = "straight"
                    elif concaveResponse == "down_concave":
                        self.down_tab = "concave"
                    elif concaveResponse == "top_concave":
                        self.top_tab = "concave"
                    elif concaveResponse == "right_concave":
                        self.right_tab = "concave"
                    elif concaveResponse == "left_concave":
                        self.left_tab = "concave"

        # end of loop, define convex
        if down_or_left and down_or_right and top_or_right and top_or_left:
            if down_or_right and down_or_left and self.down_tab is None:
                self.down_tab = "convex"
            if down_or_right and top_or_right and self.right_tab is None:
                self.right_tab = "convex"
            if top_or_right and top_or_left and self.top_tab is None:
                self.top_tab = "convex"
            if down_or_left and top_or_left and self.left_tab is None:
                self.left_tab = "convex"
        else:
            if down_or_right and down_or_left:
                self.down_tab = "convex"
            if down_or_right and top_or_right:
                self.right_tab = "convex"
            if top_or_right and top_or_left:
                self.top_tab = "convex"
            if down_or_left and top_or_left:
                self.left_tab = "convex"

        if self.top_tab is None:
            self.top_tab = "straight"
        if self.down_tab is None:
            self.down_tab = "straight"
        if self.left_tab is None:
            self.left_tab = "straight"
        if self.right_tab is None:
            self.right_tab = "straight"

    def get_straight_tab_number(self):
        counter = 0
        if self.right_tab == "straight":
            counter += 1
        if self.left_tab == "straight":
            counter += 1
        if self.top_tab == "straight":
            counter += 1
        if self.down_tab == "straight":
            counter += 1
        return counter


class Trace:
    def __init__(self):
        self.start = None
        self.end = None
        self.far = None

    def __str__(self):
        return "TRACE{ start=" + str(self.start) + ", end=" + str(self.end) + ", far=" + str(self.far) + "}"

    def define_slope_angle_and_distance(self, threshold):
        # tg(alfa) = (y2-y1)/(x2-x1)
        distance_between_poitns = math.sqrt(pow(self.start[0] - self.end[0], 2) + pow(self.start[1] - self.end[1], 2))

        tangensValue = 0
        if self.end[1] < self.start[1]:
            x_lenght = self.end[0] - self.start[0]
            if x_lenght == 0:
                x_lenght = 0.00001
            tangensValue = (self.end[1] - self.start[1]) / x_lenght
        else:
            x_lenght = self.start[0] - self.end[0]
            if x_lenght == 0:
                x_lenght = 0.00001
            tangensValue = (self.start[1] - self.end[1]) / x_lenght
        degree = -math.degrees(math.atan(tangensValue))
        if degree > 0:
            if self.start[0] > self.end[0]:
                degree += 180
        else:
            if self.start[0] > self.end[0]:
                degree += 180
            else:
                degree += 360
        return degree, distance_between_poitns

    def is_on_start_and_end_line(self, threshold):
        degree, distance = self.define_slope_angle_and_distance(threshold=threshold)
        # horizontally
        if (0 <= degree <= 10) or (170 <= degree <= 190) or (350 <= degree <= 360):
            # is straight
            if (abs(self.start[1] - self.far[1]) < threshold) or (abs(self.end[1] - self.far[1]) < threshold):
                if self.start[0] > self.end[0]:
                    return "straight_top"
                else:
                    return "straight_down"
            else:
                # is concave
                if self.far[1] < self.end[1] and self.far[1] < self.start[1]:
                    return "down_concave"
                elif self.far[1] > self.end[1] and self.far[1] > self.start[1]:
                    return "top_concave"
                else:
                    return "IDK"
        # perpendicularly
        else:
            # is straight
            if (abs(self.start[0] - self.far[0]) < threshold) or (abs(self.end[0] - self.far[0]) < threshold):
                if self.start[1] > self.end[1]:
                    return "straight_right"
                else:
                    return "straight_left"
            else:
                # is concave
                if self.far[0] < self.end[0] and self.far[0] < self.start[0]:
                    return "right_concave"
                elif self.far[0] > self.end[0] and self.far[0] > self.start[0]:
                    return "left_concave"
                else:
                    return "IDK"
