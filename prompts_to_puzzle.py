import cv2
import numpy as np

FLANN_INDEX_KDTREE = 0
MIN_MATCH_COUNT = 10


def read_image(path):
    return cv2.imread(path)


def resize_image(data, label_height, label_width):
    if type(data) == str:
        image = cv2.imread(data)
        resize = image
    else:
        image = data
        resize = data
    x = 0.9
    y = 0.9
    while True:
        height, width, _ = resize.shape
        if height > label_height or width > label_width:
            resize = cv2.resize(image, (0, 0), fx=x, fy=y)
            x = x - 0.05
            y = y - 0.05
        else:
            break
    return resize


def blur_image(image, amount=3):
    kernel = np.ones((amount, amount), np.float32) / (amount**2)
    return cv2.filter2D(image, -1, kernel)


def get_contours(path_to_shuffle_image, min_value, max_value):
    image_gray = cv2.imread(path_to_shuffle_image, 0)
    image_color = cv2.imread(path_to_shuffle_image)
    image_blurred = cv2.GaussianBlur(image_gray, (1, 1), 1.5)
    image_canny = cv2.Canny(image_blurred, min_value, max_value)
    _, contours, _ = cv2.findContours(blur_image(image_canny), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(image_color, contours, -1, (0, 255, 0), 3)
    big_contours = []
    for contour in contours:
        if cv2.contourArea(contour)>3000:
            big_contours.append(contour)
    image_color = resize_image(image_color, 261, 711)
    return big_contours, image_color


def crop_image(path, contour):
    image = cv2.imread(path)
    mask = np.zeros(image.shape, dtype=np.uint8)
    roi_corners = np.array(contour, dtype=np.int32)
    channel_count = image.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    x1 = int(box[0][0])
    x2 = int(box[2][0])
    y1 = int(box[1][1])
    y2 = int(box[0][1])
    contour_image = image[y1:y2, x1:x2].copy()
    return contour_image


def prompt_location(path_to_shuffle_image, path_to_solved_image, contours):
    contours_results = []
    for contour in contours:
        image = crop_image(path_to_shuffle_image, contour)
        contours_results.append(image)
    solved_image = cv2.imread(path_to_solved_image)
    prompt_results = []
    for contour in contours_results:
        prompt_result = return_image_with_prompt(solved_image, contour)
        if prompt_result is not None:
            prompt_results.append(prompt_result)
        else:
            pass
    return prompt_results


def return_image_with_prompt(solved_image, contour_image):
    contour_image_gray = cv2.cvtColor(contour_image, cv2.COLOR_BGR2GRAY)
    solved_image_gray = cv2.cvtColor(solved_image, cv2.COLOR_BGR2GRAY)
    solved_image_copy = solved_image.copy()
    sift = cv2.xfeatures2d.SIFT_create()
    try:
        contour_image_key_points, contour_image_description = sift.detectAndCompute(contour_image_gray, None)
        solved_image_key_points, solved_image_description = sift.detectAndCompute(solved_image_gray, None)
    except cv2.error:
        return None
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50)
    flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = flann.knnMatch(contour_image_description, solved_image_description, k=2)
    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
    if len(good_matches) > MIN_MATCH_COUNT:
        src_pts = np.float32([contour_image_key_points[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([solved_image_key_points[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        matches_mask = mask.ravel().tolist()
        h, w = contour_image_gray.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)
        solved_image_copy = cv2.polylines(solved_image_copy, [np.int32(dst)], True, 255, 3, cv2.LINE_AA)
    else:
        return None
    draw_params = dict(matchColor=(0, 255, 0),
                       singlePointColor=None,
                       matchesMask=matches_mask,
                       flags=2)
    prompt_image = cv2.drawMatches(contour_image, contour_image_key_points, solved_image_copy,
                                   solved_image_key_points, good_matches, None, **draw_params)
    return prompt_image
