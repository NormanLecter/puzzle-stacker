import cv2
import numpy as np
from matplotlib import pyplot as plt

def crop_image(contour):
    image = cv2.imread('wszystkie.jpg', -1)
    mask = np.zeros(image.shape, dtype=np.uint8)
    roi_corners = np.array(contour, dtype=np.int32)
    channel_count = image.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    masked_image = cv2.resize(masked_image, (0, 0), fx=0.18, fy=0.18)
    epsilon = 0.1 * cv2.arcLength(contour, True)
    print(epsilon)
    cv2.imshow('dst', masked_image)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

def get_contours():
    canvas = cv2.imread('all.jpg')
    piece_c = cv2.imread('wszystkie.jpg')
    piece = cv2.cvtColor(piece_c, cv2.COLOR_BGR2GRAY)
    th3 = cv2.adaptiveThreshold(piece,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                                cv2.THRESH_BINARY_INV,39, 3)
    im2, contours, hierarchy = cv2.findContours(th3,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(piece_c, contours, -1, (0, 255, 0), 3)
    piece_c = cv2.resize(piece_c, (0, 0), fx=0.18, fy=0.18)
    cv2.imshow('dst', piece_c)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
    for con in contours:
        if cv2.contourArea(con)>10000:
            crop_image(con)

if __name__ == "__main__":
    get_contours()