# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- TypeCasting -- #
from numpy import ndarray

# --// PROGRAMM \\-- #
def createNormalCoordsFromContour(contour: ndarray):
    x, y, w, h = cv.boundingRect(contour)
    return x, y, x+w, y+h