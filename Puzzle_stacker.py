import cv2
import numpy as np


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
            resize = cv2.resize(image, (0,0), fx=x, fy=y)
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


def crop_image(path, contour, i):
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
    contour_image = image[y1:y2, x1:x2]
    cv2.imwrite(str(i) + '.jpg', contour_image)
    #return contour_image
    #cv2.drawContours(image, [box], 0, (0, 0, 255), 2)


# if __name__ == "__main__":
#     image = cv2.imread('pies.jpg', -1)
#     contours, _ = get_contours('pies.jpg', 40,70)
#     i = 0
#     for con in contours:
#         crop_image('pies.jpg', con, i)
#         i = i + 1
    # image = resize_image(image, 261, 711)
    # cv2.imshow("cropped", image)
    # if cv2.waitKey(0) & 0xff == 27:
    #     cv2.destroyAllWindows()
    # im = resize_image(image)
    # cv2.imshow("cropped", im)
    # if cv2.waitKey(0) & 0xff == 27:
    #     cv2.destroyAllWindows()
