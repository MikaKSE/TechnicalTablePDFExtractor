# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- TypeCasting -- #
from numpy import ndarray


# --// PROGRAMM \\-- #
class Contour:
    def __init__(self, coords: ndarray) -> None:
        self.coords: ndarray = coords
        self.next: Contour | None = None
        self.previous: Contour | None = None
        self.child: Contour | None = None
        self.parent: Contour | None = None
        self.level: int = 0
        self.rectangle: list[int] | None = None
        self.createRectangleCoords()


    def __str__(self) -> str:
        parts = []
        if self.next is not None:
            parts.append(f'next: {self.next.level}')
        if self.previous is not None:
            parts.append(f'previous: {self.previous.level}')
        if self.child is not None:
            parts.append(f'child: {self.child.level}')
        if self.parent is not None:
            parts.append(f'parent: {self.parent.level}')
        return 'Contour(' + ', '.join(parts) + ')'


    def createRectangleCoords(self) -> None:
        x, y, w, h = cv.boundingRect(self.coords)
        x1 = x
        y1 = y
        x2 = x + w
        y2 = y + h
        self.rectangle = [x1, y1, x2, y2]