# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- TypeCasting -- #
from numpy import ndarray

# -- Classes -- #
from classes.Page import Page
from classes.Table import Table


# --// PROGRAMM \\-- #
def cropTable(page: Page, table: Table, crop_buffer: int = 3):
    table.image = page.image[table.y1 - crop_buffer:table.y2 + crop_buffer,
                  table.x1 - crop_buffer:table.x2 + crop_buffer]


def detectXLines(thresh: ndarray) -> list[tuple[int, int, int, int]]:
    def extractCoordsFromContour(c) -> (int, int, int):
        x, y, w, h = cv.boundingRect(c)

        x1: int = x
        y1: int = y
        x2: int = x + w - 1
        y2: int = y + h - 1

        y = int(round((y1 + y2) / 2, 0))

        return x1, x2, y

    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (25, 1))
    horizontal = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv.findContours(horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]

    lines = []
    for c in cnts:
        x1, x2, y = extractCoordsFromContour(c)
        lines.append((x1, y, x2, y))

    return lines


def detectYLines(thresh: ndarray) -> list[tuple[int, int, int, int]]:
    def extractCoordsFromContour(c) -> (int, int, int):
        x, y, w, h = cv.boundingRect(c)

        x1: int = x
        y1: int = y - 2
        x2: int = x + w - 1
        y2: int = y - 2 + h - 1

        x = int(round((x1 + x2) / 2, 0))

        return y1, y2, x

    horizontal_kernel = cv.getStructuringElement(cv.MORPH_RECT, (1, 25))
    horizontal = cv.morphologyEx(thresh, cv.MORPH_OPEN, horizontal_kernel, iterations=2)
    cnts = cv.findContours(horizontal, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    lines = []
    for c in cnts:
        y1, y2, x = extractCoordsFromContour(c)
        lines.append((x, y1, x, y2))

    return lines


def findLeftDeadEnds(x_lines: list[tuple[int, int, int, int]], y_lines: list[tuple[int, int, int, int]],
                     x_tol: int = 10, y_tol: int = 5) -> list[tuple[int, int, int, int]]:
    dead_end_lines = []
    for x_line in x_lines:
        is_dead_end = True
        for y_line in y_lines:

            if 0 <= abs(x_line[0] - y_line[0]) <= x_tol and y_line[1] - y_tol <= x_line[1] <= y_line[3] + y_tol:
                is_dead_end = False
            else:
                is_dead_end = True

        if is_dead_end:
            dead_end_lines.append(x_line)

    return dead_end_lines


def findRightDeadEnds(x_lines: list[tuple[int, int, int, int]], y_lines: list[tuple[int, int, int, int]],
                      x_tol: int = 10, y_tol: int = 5) -> list[tuple[int, int, int, int]]:
    dead_end_lines = []
    for x_line in x_lines:
        is_dead_end = True
        for y_line in y_lines:

            if 0 <= abs(x_line[2] - y_line[2]) <= x_tol and y_line[1] - y_tol <= x_line[1] <= y_line[3] + y_tol:
                is_dead_end = False

        if is_dead_end:
            dead_end_lines.append(x_line)

    return dead_end_lines


def findDeadEndVerticalLines(x_lines: list[tuple[int, int, int, int]], dead_end_lines: list[tuple[int, int, int, int]]): # lower and upper vertauscht
    new_dead_end_vertical_lines = set()
    for d_line in dead_end_lines:
        upper = []
        lower = []

        for x_line in reversed(x_lines):
            if x_line[0] < d_line[0] < x_line[2] and d_line[1] < x_line[1]:
                lower = x_line
                break

        for x_line in x_lines:
            if x_line[0] < d_line[0] < x_line[2] and d_line[1] > x_line[1]:
                upper = x_line
                break

        if lower and upper:
            new_dead_end_vertical_lines.add((d_line[0], upper[1], d_line[0], lower[3]))
        else:
            for x_line in reversed(x_lines):
                if x_line[0] < d_line[2] < x_line[2] and d_line[1] < x_line[1]:
                    lower = x_line
                    break

            for x_line in x_lines:
                if x_line[0] < d_line[2] < x_line[2] and d_line[1] > x_line[1]:
                    upper = x_line
                    break

            new_dead_end_vertical_lines.add((d_line[2], upper[1], d_line[2], lower[3]))

    return new_dead_end_vertical_lines