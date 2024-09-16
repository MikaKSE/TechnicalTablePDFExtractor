# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv

# -- Classes -- #
from classes.Table import Table
from classes.Element import Element


# --// PROGRAMM \\-- #
def sortElements(table: Table):
    def custom_sort_key(element):  # Define a custom sorting key function
        return element.y1, element.x2, element.y2, element.x2

    table.elements = sorted(table.elements, key=custom_sort_key)


def createFormattedElementCoords(table: Table, border_size: int):
    for e in table.elements:
        e.createFormattedCoords(table, border_size)


def createDistinctValues(x_lines: list[tuple[int, int, int, int]], y_lines: list[tuple[int, int, int, int]]) -> (list[tuple[int]], list[tuple[int]]):
    distinct_x = sorted(set(x_line[1] for x_line in x_lines))
    distinct_y = sorted(set(y_line[0] for y_line in y_lines))
    return distinct_x, distinct_y


def findClosestXLines(e: Element, x_lines: list[tuple[int, int, int, int]]):
    closest_line1: tuple = ()
    closest_line2: tuple = ()
    for x_line1 in x_lines:
        for x_line2 in x_lines:
            if x_line1[1] < x_line2[1]:  # Line1 ist above line2
                if x_line1[0] < e.fv_mid[0] < x_line1[2] and x_line2[0] < e.fv_mid[0] < x_line2[2]:  # Elements h_midline is between the width of line1 and line2
                    if x_line1[1] <= e.fh_mid[1] <= x_line2[1]:  # Elements v_midline is between the height of line1 and line2

                        if closest_line1:
                            r1 = closest_line2[1] - closest_line1[1]
                            r2 = x_line2[1] - x_line1[1]
                            if r2 < r1:  # Checks the distance if the new line pair if it is smaller
                                closest_line1 = x_line1
                                closest_line2 = x_line2
                        else:
                            closest_line1 = x_line1
                            closest_line2 = x_line2

    return closest_line1, closest_line2


def findClosestYLines(e: Element, y_lines: list[tuple[int, int, int, int]]):
    closest_line1: tuple = ()
    closest_line2: tuple = ()
    for y_line1 in y_lines:
        for y_line2 in y_lines:
            if y_line1[0] < y_line2[0]:
                if y_line1[1] < e.fh_mid[1] < y_line1[3] and y_line2[1] < e.fh_mid[1] < y_line2[3]:
                    if y_line1[0] <= e.fv_mid[0] <= y_line2[0]:

                        if closest_line1:
                            r1 = closest_line2[0] - closest_line1[0]
                            r2 = y_line2[0] - y_line1[0]
                            if r2 < r1:
                                closest_line1 = y_line1
                                closest_line2 = y_line2
                        else:
                            closest_line1 = y_line1
                            closest_line2 = y_line2
    return closest_line1, closest_line2


def sortAssignedElements(table: Table):
    def sort_key(element):
        return element.row, element.column, element.x1, element.y1
    table.elements.sort(key=sort_key)


def assignElements(table: Table):
    distinct_x, distinct_y = createDistinctValues(table.x_lines, table.y_lines)

    def remove_close_values(distinct_x, threshold=10):
        # Sortiere das Array
        distinct_x.sort()

        # Initialisiere das Ergebnis-Array mit dem ersten Element
        result = [distinct_x[0]]

        # Iteriere durch das Array und füge nur Werte hinzu, die nicht innerhalb des Abstands liegen
        for value in distinct_x[1:]:
            if value - result[-1] > threshold:
                result.append(value)

        return result

    distinct_y = remove_close_values(distinct_y, threshold=5)

    for e in table.elements:

        x_line1, x_line2 = findClosestXLines(e, table.x_lines)

        for i, dx in enumerate(distinct_x):
            if x_line1[1] < dx <= x_line2[1]:
                e.row.append(i-1)

        y_line1, y_line2 = findClosestYLines(e, table.y_lines)

        for i, dy in enumerate(distinct_y):
            if y_line1[0] < dy <= y_line2[0]:
                e.column.append(i-1)