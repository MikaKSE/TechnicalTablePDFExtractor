# --// IMPORTS \\-- #
# -- Libraries -- #
import sys
sys.setrecursionlimit(5000)

# -- Classes -- #
from classes.Contour import Contour


# --// PROGRAMM \\-- #
def createContourObjects(contours, hierarchies) -> list[Contour]:
    contour_objects: list[Contour] = [Contour(contour) for contour in contours]

    for idx, hierarchy in enumerate(hierarchies[0]):
        next_idx, previous_idx, child_idx, parent_idx = hierarchy

        if next_idx != -1:
            contour_objects[idx].next = contour_objects[next_idx]
        if previous_idx != -1:
            contour_objects[idx].previous = contour_objects[previous_idx]
        if child_idx != -1:
            contour_objects[idx].child = contour_objects[child_idx]
        if parent_idx != -1:
            contour_objects[idx].parent = contour_objects[parent_idx]

    return contour_objects


def setContourLevels(contour_objects: list[Contour]) -> None:  # not used
    def calculate_level(contour_obj: Contour, current_level: int):
        contour_obj.level = current_level
        if contour_obj.child:
            calculate_level(contour_obj.child, current_level + 1)
        if contour_obj.next:
            calculate_level(contour_obj.next, current_level)

    for contour_obj in contour_objects:
        if contour_obj.parent is None:  # Start at the root contours
            calculate_level(contour_obj, 0)