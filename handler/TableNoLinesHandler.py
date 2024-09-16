# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv
from collections import defaultdict

# -- TypeCasting -- #
from numpy import ndarray

# -- Classes -- #
from classes.Table import Table


# --// PROGRAMM \\-- #
def detect_dilate_boxes(img_dilate: ndarray) -> list[tuple[int, int, int, int]]:
    cnts = cv.findContours(img_dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)[0]

    cnts = sorted(cnts, key=lambda x: cv.boundingRect(x)[0])

    boxes = []
    for cnt in cnts:
        x, y, w, h = cv.boundingRect(cnt)
        x1, y1 = x, y
        x2, y2 = x + w, y + h
        boxes.append((x1, y1, x2, y2))

    return boxes


def sortXBoxes(table: Table) -> None:
    table.x_boxes = sorted(table.x_boxes, key=lambda x: x[1])


def determineRow(table: Table) -> None:
    for e in table.elements:
        for i, box in enumerate(table.x_boxes):
            if box[0] <= e.fv_mid[0] <= box[2] and box[1] <= e.fh_mid[1] <= box[3]:
                e.row = [i]


def sortYBoxes(table: Table) -> None:
    table.y_boxes = sorted(table.y_boxes, key=lambda x: x[0])


def determineColumn(table: Table) -> None:
    tol = 20
    for e in table.elements:
        for i, box in enumerate(table.y_boxes):
            if e.fh_mid[0]+tol >= box[0] and e.fh_mid[1]+tol >= box[1] and e.fh_mid[2]-tol <= box[2] and e.fh_mid[3]-tol <= box[3]:
                e.column = [i]


def checkAlignment(table: Table) -> None:
    # Dictionary to store elements by their row[0] value
    row_groups = defaultdict(list)

    # Group elements by their row[0] value
    for e in table.elements:
        row_groups[e.column[0]].append(e)


    # Check alignment for each group
    for row_key, elements in row_groups.items():
        if len(elements) < 2:
            continue  # Skip groups with less than 2 elements

        # Count how many elements have the same fx1 value
        fx1_counts = defaultdict(int)
        for e in elements:
            fx1_counts[e.fx1] += 1

        # Find the most common fx1 value
        most_common_fx1, most_common_count = max(fx1_counts.items(), key=lambda item: item[1])

        # Check if 70% or more elements have the most common fx1 value
        if most_common_count / len(elements) >= 0.7:
            for e in elements:
                e.alignment = "left"


def rearrangeIndentedElements(table):
    cols = set()
    for e in table.elements:
        cols.add(e.column[0])
    for col in cols:
        found = False
        found_elements = []

        for e in table.elements:
            if e.column[0] == col:
                if e.fx1 > table.y_boxes[col][0] + 50 and e.alignment == "left":
                    found = True
                    found_elements.append(e)

        if found:
            for e2 in table.elements:
                if e2.column[0] > col:
                    e2.column[0] += 1
            for e3 in found_elements:
                e3.column[0] = col + 1