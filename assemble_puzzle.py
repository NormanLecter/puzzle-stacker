import cv2
import numpy as np
import copy
from PIL import Image

from assemble_puzzle_classes import SinglePuzzle, Trace

puzzle_solving_thread_list = []


def blur_image(image, amount=3):
    # Blurs the image
    # Does not affect the original image
    kernel = np.ones((amount, amount), np.float32) / (amount ** 2)
    return cv2.filter2D(image, -1, kernel)


def try_to_assemble_puzzles(filename, contours):
    base_image_color = cv2.imread(filename)
    single_puzzles = []
    for con in contours:
        if cv2.contourArea(con) > 3000:
            single_puzzle = mask_image(con, filename)
            single_puzzles.append(single_puzzle)

    width, height = base_image_color.shape[:2]
    assembled_puzzle = assemble_the_puzzles(single_puzzles, width, height)
    return assembled_puzzle


def mask_image(contour, image_path):
    image = cv2.imread(image_path, -1)

    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    x_values = [box[0][0], box[1][0], box[2][0], box[3][0]]
    y_values = [box[0][1], box[1][1], box[2][1], box[3][1]]
    x1 = min(x_values)
    x2 = max(x_values)
    y1 = min(y_values)
    y2 = max(y_values)

    cv2.drawContours(image, [box], 0, (0, 0, 255), 2)

    crop_img = image[y1:y2, x1:x2]
    single_puzzle = find_puzzle_tabs(contour, image)
    single_puzzle.crop_image = crop_img
    single_puzzle.threshold = (y2 - y1) / 10  # 10% of puzzle height
    single_puzzle.define_puzzle_tabs()

    return single_puzzle


def find_puzzle_tabs(contour, img):
    hull = cv2.convexHull(contour, returnPoints=False)

    defects = cv2.convexityDefects(contour, hull)

    single_puzzle = SinglePuzzle()

    for i in range(defects.shape[0]):
        s, e, f, d = defects[i, 0]
        start = tuple(contour[s][0])
        end = tuple(contour[e][0])
        far = tuple(contour[f][0])
        trace = Trace()
        trace.start = start
        trace.end = end
        trace.far = far
        single_puzzle.traces.append(trace)

        cv2.line(img, start, end, [0, 255, 0], 2)
        cv2.circle(img, far, 5, [255, 0, 0], -1)
    return single_puzzle


def assemble_the_puzzles(single_puzzles, width, height):
    corners_puzzles = []
    border_puzzles_top = []
    border_puzzles_down = []
    border_puzzles_left = []
    border_puzzles_right = []
    inside_puzzles = []
    for single_puzzle in single_puzzles:
        straight_tab_number = single_puzzle.get_straight_tab_number()
        if straight_tab_number == 2:
            corners_puzzles.append(single_puzzle)
        elif straight_tab_number == 1:
            if single_puzzle.top_tab == "straight":
                border_puzzles_top.append(single_puzzle)
            elif single_puzzle.down_tab == "straight":
                border_puzzles_down.append(single_puzzle)
            elif single_puzzle.right_tab == "straight":
                border_puzzles_right.append(single_puzzle)
            elif single_puzzle.left_tab == "straight":
                border_puzzles_left.append(single_puzzle)
        elif straight_tab_number == 0:
            inside_puzzles.append(single_puzzle)
    final_puzzles_width = 2 + len(border_puzzles_top)
    final_puzzles_height = 2 + len(border_puzzles_right)
    # create array of size of puzzles(one array value is one puzzle)
    final_puzzles = [[0 for x in range(final_puzzles_width)] for y in range(final_puzzles_height)]

    for corner in corners_puzzles:
        if corner.top_tab == "straight":
            if corner.right_tab == "straight":
                final_puzzles[0][final_puzzles_width - 1] = corner
            else:
                final_puzzles[0][0] = corner
        else:
            if corner.right_tab == "straight":
                final_puzzles[final_puzzles_height - 1][final_puzzles_width - 1] = corner
            else:
                final_puzzles[final_puzzles_height - 1][0] = corner

    unfitted_puzzles = []
    unfitted_puzzles.extend(border_puzzles_top)
    unfitted_puzzles.extend(border_puzzles_down)
    unfitted_puzzles.extend(border_puzzles_left)
    unfitted_puzzles.extend(border_puzzles_right)
    unfitted_puzzles.extend(inside_puzzles)

    additional_final_puzzles = []
    x = 0
    y = 0
    while x < final_puzzles_width:
        while y < final_puzzles_height:
            if final_puzzles[y][x] == 0:
                additional_final = complete_field(final_puzzles, unfitted_puzzles, x, y, final_puzzles_width,
                                                  final_puzzles_height)
                if additional_final is not None and additional_final != "ERROR":
                    additional_final_puzzles.append(additional_final)

                if additional_final == "ERROR":
                    additional_tuple = additional_final_puzzles.pop()

                    final_puzzles = additional_tuple[0]
                    x = additional_tuple[1]
                    y = additional_tuple[2]
            y += 1
        x += 1
        y = 0

    image = Image.new("RGBA", (width + 500, height))
    actual_height = 0
    actual_width = 0
    max_width = 0
    for y in range(len(final_puzzles)):
        y_values = []
        for x in range(len(final_puzzles[y])):
            temp_image = Image.fromarray(final_puzzles[y][x].crop_image)
            image.paste(temp_image, (actual_width, actual_height))
            width, height = temp_image.size
            actual_width += width

            y_values.append(height)
        if actual_width > max_width:
            max_width = actual_width
        actual_width = 0
        actual_height += max(y_values)

    open_cv_image = np.array(image)
    trimmed_image = open_cv_image[0:actual_height, 0:max_width]
    return np.array(trimmed_image)


def complete_field(final_puzzles, unfitted_puzzles, horizontal_position, perpendicularly_position, horizontal_array_size,
                   perpendicularly_array_size):
    single_puzzle_left = "straight"
    single_puzzle_right = "straight"
    single_puzzle_top = "straight"
    single_puzzle_down = "straight"

    if horizontal_position != 0:
        single_puzzle_left = final_puzzles[perpendicularly_position][horizontal_position - 1]
    if horizontal_position != (horizontal_array_size - 1):
        single_puzzle_right = final_puzzles[perpendicularly_position][horizontal_position + 1]

    if perpendicularly_position != 0:
        single_puzzle_top = final_puzzles[perpendicularly_position - 1][horizontal_position]
    if perpendicularly_position != (perpendicularly_array_size - 1):
        single_puzzle_down = final_puzzles[perpendicularly_position + 1][horizontal_position]

    puzzles_that_can_fit = []
    for puzzle in unfitted_puzzles:

        if single_puzzle_left != "straight" and single_puzzle_right != "straight" and single_puzzle_top != "straight"\
                and single_puzzle_down != "straight":
            if puzzle.left_tab == "straight" or puzzle.right_tab == "straight" or puzzle.top_tab == "straight"\
                    or puzzle.down_tab == "straight":
                continue

        if single_puzzle_left == "straight":
            if puzzle.left_tab != "straight":
                continue
        elif single_puzzle_left != 0:
            if not (
                    single_puzzle_left.right_tab != "straight" and puzzle.left_tab != "straight"
                    and single_puzzle_left.right_tab != puzzle.left_tab):
                continue

        if single_puzzle_right == "straight":
            if puzzle.right_tab != "straight":
                continue
        elif single_puzzle_right != 0:
            if not (
                    single_puzzle_right.left_tab != "straight" and puzzle.right_tab != "straight"
                    and single_puzzle_right.left_tab != puzzle.right_tab):
                continue

        if single_puzzle_top == "straight":
            if puzzle.top_tab != "straight":
                continue
        elif single_puzzle_top != 0:
            if not (
                    single_puzzle_top.down_tab != "straight" and puzzle.top_tab != "straight"
                    and single_puzzle_top.down_tab != puzzle.top_tab):
                continue

        if single_puzzle_down == "straight":
            if puzzle.down_tab != "straight":
                continue
        elif single_puzzle_down != 0:
            if not (
                    single_puzzle_down.top_tab != "straight" and puzzle.down_tab != "straight"
                    and single_puzzle_down.top_tab != puzzle.down_tab):
                continue
        puzzles_that_can_fit.append(puzzle)

    if len(puzzles_that_can_fit) == 0:
        return "ERROR"

    final_puzzles[perpendicularly_position][horizontal_position] = puzzles_that_can_fit[0]

    if len(puzzles_that_can_fit) > 1:
        additionalArray = copy.deepcopy(final_puzzles)
        additionalArray[perpendicularly_position][horizontal_position] = puzzles_that_can_fit[1]
        additional = (additionalArray, horizontal_position, perpendicularly_position)
        return additional

    return None
