import cv2
import numpy as np


def blur_image(image, amount=3):
    kernel = np.ones((amount, amount), np.float32) / (amount**2)
    return cv2.filter2D(image, -1, kernel)

def get_contours():

    def progowanie(x):
        print("Progowanie: " + str(x))

    def rozmycie(x):
        print("rozmycie: " + str(x))

    img = cv2.imread('pies.jpg', 0)
    img_c = cv2.imread('pies.jpg')

    cv2.namedWindow('image')

    cv2.createTrackbar('progowanie1', 'image', 39, 255, progowanie)

    cv2.createTrackbar('progowanie2', 'image', 38, 255, progowanie)

    cv2.createTrackbar('rozmycie', 'image', 1, 7, rozmycie)

    imgshow = img

    while (1):
        cv2.imshow('image', imgshow)
        k = cv2.waitKey(1) & 0xFF
        if k == 27:
            break
        progowanie1 = cv2.getTrackbarPos('progowanie1', 'image')

        progowanie2 = cv2.getTrackbarPos('progowanie2', 'image')

        blur = cv2.getTrackbarPos('rozmycie', 'image')

        if blur % 2 == 0:
            blur = blur + 1
        bluredImg = cv2.GaussianBlur(img, (blur, blur), 1.5)
        imgshow = cv2.Canny(bluredImg, progowanie1, progowanie2)


    im2, contours, hierarchy = cv2.findContours(blur_image(imgshow), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(img_c, contours, -1, (0, 255, 0), 3)
    cv2.imshow('dst', img_c)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()
    for con in contours:
        if cv2.contourArea(con)>3000:
            crop_image(con)


def mask_image(contour):
    image = cv2.imread('pies.jpg', -1)
    mask = np.zeros(image.shape, dtype=np.uint8)
    roi_corners = np.array(contour, dtype=np.int32)
    channel_count = image.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    cv2.imshow('dst', masked_image)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()


def crop_image(contour):
    image = cv2.imread('pies.jpg', -1)
    mask = np.zeros(image.shape, dtype=np.uint8)
    roi_corners = np.array(contour, dtype=np.int32)
    channel_count = image.shape[2]
    ignore_mask_color = (255,) * channel_count
    cv2.fillConvexPoly(mask, roi_corners, ignore_mask_color)
    masked_image = cv2.bitwise_and(image, mask)
    epsilon = 0.1 * cv2.arcLength(contour, True)
    print("/n/n/n/n/n/n/n/n/nNew single puzzle:")
    print(contour)
    rect = cv2.minAreaRect(contour)
    print("box:")
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    print(box)
    x1 = int(box[0][0])
    x2 = int(box[2][0])
    y1 = int(box[1][1])
    y2 = int(box[0][1])
    # print(rect[0][0])
    # print(rect[0][1])
    # print(rect[1][0])
    # print(rect[1][1])
    print(x1)
    print(x2)
    print(y1)
    print(y2)

    print(box)
    crop_img = image[y1:y2, x1:x2]
    cv2.imshow("cropped", crop_img)
    cv2.waitKey(0)
    cv2.drawContours(image, [box], 0, (0, 0, 255), 2)
    print("/n/n/n/n/n/n/n/n/n")
    cv2.imshow('dst', image)
    if cv2.waitKey(0) & 0xff == 27:
        cv2.destroyAllWindows()

if __name__ == "__main__":
    get_contours()