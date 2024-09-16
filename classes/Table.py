# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv
import utils

# -- TypeCasting -- #
from numpy import ndarray

# -- Classes -- #
from classes import Element
from classes.Contour import Contour


# --// PROGRAMM \\-- #
class Table:
    def __init__(self, has_lines, contour: Contour | None = None, x1: int | None = None, y1: int | None = None, x2: int | None = None, y2: int | None = None):
        self.contour: Contour = contour
        if contour:
            self.x1, self.y1, self.x2, self.y2 = utils.createNormalCoordsFromContour(contour.coords)
        else:
            self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2
        self.nr: int | None = None
        self.elements: list[Element] = []
        self.has_lines: bool = has_lines
        self.image: ndarray | None = None
        self.img_border: ndarray | None = None
        self.img_gray: ndarray | None = None
        self.img_thresh: ndarray | None = None
        self.img_row_dilate: ndarray | None = None
        self.img_col_dilate: ndarray | None = None
        self.x_lines: list[tuple[int, int, int, int]] = []
        self.y_lines: list[tuple[int, int, int, int]] = []
        self.x_boxes: list[tuple[int, int, int, int]] = []
        self.y_boxes: list[tuple[int, int, int, int]] = []
        self.dead_end_lines: list[tuple[int, int, int, int]] = []
        self.dead_end_vertical_lines: list[tuple[int, int, int, int]] = []


    def __str__(self):
        return (
            f'Table({self.x1}, {self.y1}, {self.x2}, {self.y2}'
        )


    # -- Functions -- #
    def showImage(self) -> None:
        cv.imshow("TableImage", self.image)
        cv.waitKey(0)


    def setElements(self, elements: list[Element]):
        for e in elements:
            if self.x1 < e.v_mid[0] < self.x2 and self.y1 < e.h_mid[1] < self.y2:
                self.elements.append(e)
                e.in_table = True