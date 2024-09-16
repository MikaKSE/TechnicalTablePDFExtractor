# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- TypeCasting -- #
from numpy import ndarray

# -- Classes -- #
from classes.Element import Element
from classes.Contour import Contour
from classes.Table import Table


# --// PROGRAMM \\-- #
class Page:
    def __init__(self, page_number: int, img_page) -> None:
        self.nr: int = page_number
        self.all_elements: list[Element] = []
        self.relevant_elements: list[Element] = []
        self.image: ndarray = img_page
        self.img_gray: ndarray | None = None
        self.img_thresh: ndarray | None = None
        self.contours_all: list[Contour] | None = None
        self.tables: list[Table] = []


    def __str__(self) -> str:
        return (
            f"Page Number: {self.nr}"
        )


    # -- Functions -- #
    def showImage(self) -> None:
        cv.imshow("Image", self.image)
        cv.waitKey(0)