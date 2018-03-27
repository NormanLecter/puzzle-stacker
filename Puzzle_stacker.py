import cv2
import numpy as np
from matplotlib import pyplot as plt


canvas = cv2.imread('all.jpg')
piece_c = cv2.imread('wszystkie.jpg')

piece = cv2.cvtColor(piece_c, cv2.COLOR_BGR2GRAY)
th3 = cv2.adaptiveThreshold(piece,255,cv2.ADAPTIVE_THRESH_MEAN_C,\
                            cv2.THRESH_BINARY_INV,39, 8)
im2, contours, hierarchy = cv2.findContours(th3,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(piece_c, contours, -1, (0, 255, 0), 3)
piece_c = cv2.resize(piece_c, (0,0), fx=0.25, fy=0.25)
cv2.imshow('dst',piece_c)
if cv2.waitKey(0) & 0xff == 27:
    cv2.destroyAllWindows()
