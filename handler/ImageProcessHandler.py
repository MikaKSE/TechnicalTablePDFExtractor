# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- TypeCasting -- #
from numpy import ndarray


# --// PROGRAMM \\-- #
def createGrayAndThresh(img_plain: ndarray) -> (ndarray, ndarray):
    img_gray = cv.cvtColor(img_plain, cv.COLOR_BGR2GRAY)
    img_thresh = cv.threshold(img_gray, 150, 255, cv.THRESH_BINARY_INV)[1]

    return img_gray, img_thresh


def findContours(img_thresh: ndarray) -> (tuple, ndarray):
    contours, hierarchies = cv.findContours(img_thresh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    return contours, hierarchies


def addBorder(image: ndarray, color: tuple = (255,255,255), border_size: int = 30) -> ndarray:
    return cv.copyMakeBorder(image, border_size, border_size, border_size, border_size, cv.BORDER_CONSTANT, value=color)


def makeImageGray(image: ndarray) -> ndarray:
    return cv.cvtColor(image, cv.COLOR_BGR2GRAY)


def makeImageThresh(img_gray: ndarray) -> ndarray:
    return cv.threshold(img_gray, 0, 255, cv.THRESH_BINARY_INV + cv.THRESH_OTSU)[1]


def makeImageDilate(img_thresh: ndarray, kernal_size: tuple) -> ndarray:
    kernal = cv.getStructuringElement(cv.MORPH_RECT, kernal_size)
    img_dilate = cv.dilate(img_thresh, kernal, iterations=1)
    return img_dilate