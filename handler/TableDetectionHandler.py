# --// IMPORTS \\-- #
# -- Libraries -- #
import cv2 as cv
from collections import Counter
import Path
import utils
import re
import sys
sys.setrecursionlimit(5000)

# -- Handler -- #
from handler import SaveImagesHandler

# -- Classes -- #
from classes.Contour import Contour
from classes.Page import Page
from classes.Table import Table
from classes.Row import Row
from classes.Element import Element
import Constants


# --// PROGRAMM \\-- #
# -- With Lines -- #
def countChildren(contour: Contour, min_area: int = 2000) -> (int, list[int], list[int]):
    child_count: int = 0
    child: Contour = contour.child
    children: list[Contour] = []

    # Count the children and filter by area
    while child is not None:
        area = cv.contourArea(child.coords)
        if area >= min_area:
            child_count += 1
            children.append(child)
        child = child.next

    # Initialize sets for x and y coordinates
    child_x = set()
    child_y = set()

    # Add the coordinates of the children
    for child in children:
        x, y, w, h = cv.boundingRect(child.coords)

        child_x.add(x)
        child_y.add(y)

        if child == children[0]:
            child_x.add(x + w)
            child_y.add(y + h)

    # Sort the coordinates
    child_x = sorted(child_x)
    child_y = sorted(child_y)

    return child_x, child_y


def countUnits(page: Page, child_x: list[int], child_y: list[int]) -> int:
    count_units: int = 0
    regex_pattern: str = Constants.unit_regex
    regex: re.Pattern = re.compile(regex_pattern)

    # Iterate through the child_x coordinates (columns)
    for i in range(len(child_x) - 1):
        count: int = 0

        for e in page.relevant_elements:
            # Check if the element is within the bounds defined by child_x and child_y
            if list(child_x)[i] < e.v_mid[0] < list(child_x)[i + 1] and list(child_y)[0] < e.h_mid[1] < list(child_y)[-1]:
                if regex.search(e.text):
                    count += 1

            # Update count_units if the current count is greater
            count_units = max(count_units, count)

    return count_units


def findTablesWithLines(contour: Contour, page: Page) -> None:
    def markElementWithTable(page: Page, x1: int, y1: int, x2: int, y2: int) -> None:
        for e in page.relevant_elements:
            if e.x1 > x1 and e.y1 > y1 and e.x2 < x2 and e.y2 < y2:
                e.in_table = True

    # Zähle die Kinder der aktuellen Kontur
    child_x, child_y = countChildren(contour)
    count_units = countUnits(page, child_x, child_y)

    if len(child_y) >= 5 and len(child_x) >= 2 and count_units != 0 and count_units / len(child_y) >= 0.2:
        page.tables.append(Table(True, contour=contour))
        x1, y1, x2, y2 = utils.createNormalCoordsFromContour(contour.coords)
        markElementWithTable(page, x1, y1, x2, y2)


def getTablesWithLines(contour: Contour, page: Page) -> None:
    def traverseContours(contour: Contour, page: Page) -> None:
        if contour is None:
            return

        findTablesWithLines(contour, page)

        # Durchlaufe die Kinder der aktuellen Kontur
        traverseContours(contour.child, page)

        # Durchlaufe die Geschwister der aktuellen Kontur
        traverseContours(contour.next, page)

    traverseContours(contour, page)


# -- Without Lines -- #
def findMostFrequent(values: list[int]) -> int | None:
    """
    Find the most frequent value in a list, ensuring it appears at least 5 times.

    Args:
        values (list[int]): List of values.

    Returns:
        int: The most frequent value or None if no value meets the criteria.
    """
    if not values:
        return None  # Return None if the list is empty
    counter = Counter(values)
    most_common = counter.most_common(1)  # Get the most common element and its frequency
    if most_common[0][1] < 5:
        return None  # Return None if the most common element appears less than 5 times
    return most_common[0][0]  # Return the most common element


def getTablesWithoutLines(page: Page) -> None:
    def createRowObjects(y1_values: list[int]) -> list[Row]:
        """
        Create Row objects from y1 values.

        Args:
            y1_values (list[int]): List of y1 values.

        Returns:
            list[Row]: List of Row objects.
        """
        return [Row(index, y1) for index, y1 in enumerate(y1_values)]

    def determineTableX1(page: Page) -> int:
        """
        Determine the most frequent x1 value from table rows that contain units.

        Args:
            page (Page): The page object containing relevant elements.

        Returns:
            int: The most frequent x1 value or -1 if no such value is found.
        """

        def extractRowLines(page: Page) -> list[int]:
            """
            Extract unique y1 values from relevant elements and sort them.

            Args:
                page (Page): The page object containing relevant elements.

            Returns:
                list[int]: Sorted list of unique y1 values.
            """
            y1_values = {element.y1 for element in page.relevant_elements}
            return sorted(y1_values)

        def assignElementsToRows(rows: list[Row], page: Page) -> None:
            """
            Assign elements to their corresponding rows based on their vertical position.

            Args:
                rows (list[Row]): List of Row objects.
                page (Page): The page object containing relevant elements.
            """
            for element in page.relevant_elements:
                for row in rows:
                    if not element.in_table and element.h_mid[1] < row.y:
                        row.elements.append(element)
                        break

        def markRowsWithUnits(rows: list[Row], unit_regex: str) -> None:
            """
            Mark rows that contain elements matching the unit regex.

            Args:
                rows (list[Row]): List of Row objects.
                unit_regex (str): Regular expression pattern for units.
            """
            pattern = re.compile(unit_regex)
            for row in rows:
                if any(pattern.search(element.text) for element in row.elements):
                    row.has_unit = True

        def extractX1Values(rows: list[Row]) -> list[int]:
            """
            Extract x1 values from rows that contain units.

            Args:
                rows (list[Row]): List of Row objects.

            Returns:
                list[int]: List of x1 values.
            """
            return [row.elements[0].x1 for row in rows if row.has_unit]

        # Main logic
        y1_values = extractRowLines(page)  # Extract and sort unique y1 values
        rows = createRowObjects(y1_values)  # Create Row objects
        assignElementsToRows(rows, page)  # Assign elements to rows based on vertical position
        markRowsWithUnits(rows, Constants.unit_regex)  # Mark rows containing units
        x1_values = extractX1Values(rows)  # Extract x1 values from rows with units
        most_frequent_x1 = findMostFrequent(x1_values)  # Find the most frequent x1 value

        # Return the most frequent x1 value or -1 if not found
        return most_frequent_x1 if most_frequent_x1 is not None else -1

    def determineUnitSpace():
        def extractRowLines(page: Page, x_value: int) -> list[int]:
            """
            Extract unique y1 values from relevant elements that are to the right of x_value and sort them.

            Args:
                page (Page): The page object containing relevant elements.
                x_value (int): The x1 value to filter elements.

            Returns:
                list[int]: Sorted list of unique y1 values.
            """
            y1_values = {element.y1 for element in page.relevant_elements if element.x1 > x_value}
            return sorted(y1_values)

        def assignElementsToRows(rows: list[Row], page: Page, x_value: int) -> None:
            """
            Assign elements to their corresponding rows based on their vertical position and x_value.

            Args:
                rows (list[Row]): List of Row objects.
                page (Page): The page object containing relevant elements.
                x_value (int): The x1 value to filter elements.
            """
            for element in page.relevant_elements:
                for row in rows:
                    if element.h_mid[1] < row.y and element.x1 > x_value:
                        row.elements.append(element)
                        break

        def cleanSubElements(elements):
            """Remove empty sub-elements from the list, preserving the original logic."""
            # Remove leading empty sub-elements
            while elements and (elements[0].text == "" or elements[0].text == " "):
                elements.pop(0)

            # Remove trailing empty sub-elements
            while elements and (elements[-1].text == "" or elements[-1].text == " "):
                elements.pop()

            return elements

        y1_values = extractRowLines(page, x1_table)
        rows = createRowObjects(y1_values)
        assignElementsToRows(rows, page, x1_table)

        regex: re.Pattern = re.compile(Constants.unit_regex)

        value_coords = []
        unit_coords = []
        unit_elements = set()
        for row in rows:
            for e in row.elements:
                match = regex.search(e.text)
                if not e.in_table and match:
                    # Extrahiere die Gruppen
                    value = match.group(1).strip() if match.group(1) else ""
                    unit = match.group(2)

                    cleanSubElements(e.sub_elements)

                    # Split the elements subelements in value and unit subelements
                    value_subelements = e.sub_elements[:len(value)]

                    value_coords.append(value_subelements[-1].x2)  # get x2 of the last value subelement

                    unit_subelements = e.sub_elements[-len(unit):]
                    unit_coords.append(unit_subelements[0].x1)  # get x1 of the frist unit subelement

                    unit_elements.add(e)

        most_freq_text = findMostFrequent(value_coords)
        most_freq_unit = findMostFrequent(unit_coords)

        return most_freq_text, most_freq_unit, list(unit_elements)

    def determineTableY1Y2(page: Page, x1_table: int, text_end_coord: int, unit_elements: list) -> (int, int):
        """
        Process table rows to find elements within specified coordinates and flatten the list of elements.

        Args:
            page (Page): The page object containing relevant elements.
            x1_table (int): The x1 coordinate to filter elements.
            text_end_coord (int): The x2 coordinate to identify text end elements.
            unit_elements (list): List of unit elements to be included in the table row elements.

        Returns:
            y1_table (int): Maximum y1 values from the flattened list of table row elements.
            y2_table (int): Minimum y2 value from the flattened list of table row elements.
        """

        def filterElementsByX1(page: Page, x1_table: int) -> list:
            """
            Filter elements by the specified x1 coordinate.

            Args:
                page (Page): The page object containing relevant elements.
                x1_table (int): The x1 coordinate to filter elements.

            Returns:
                list: List of elements with the specified x1 coordinate.
            """
            return [e for e in page.relevant_elements if e.x1 == x1_table]

        def findBoundaryElements(elements: list) -> tuple:
            """
            Find the first and last elements in the list.

            Args:
                elements (list): List of elements.

            Returns:
                tuple: First and last elements in the list.
            """
            return elements[0], elements[-1]

        def collectTextEndWords(page: Page, first_element: Element, last_element: Element, x1_table: int, text_end_coord: int) -> list:
            """
            Collect elements that are within the specified y and x coordinates and have the specified x2 coordinate.

            Args:
                page (Page): The page object containing relevant elements.
                first_element (Element): The first element with the specified x1 coordinate.
                last_element (Element): The last element with the specified x1 coordinate.
                x1_table (int): The x1 coordinate to filter elements.
                text_end_coord (int): The x2 coordinate to identify text end elements.

            Returns:
                list: List of elements that match the criteria.
            """
            text_end_words = []
            for e in page.relevant_elements:
                if e.y1 >= first_element.y1 and e.y2 <= last_element.y2 and e.x1 >= x1_table:
                    if e.x2 == text_end_coord:
                        text_end_words.append(e)
            return text_end_words

        def flattenElementList(elements: list) -> list:
            """
            Flatten a list of elements, ensuring no nested lists remain.

            Args:
                elements (list): List of elements, potentially containing nested lists.

            Returns:
                list: Flattened list of elements.
            """
            flat_list = []
            for item in elements:
                if isinstance(item, list):
                    flat_list.extend(item)
                else:
                    flat_list.append(item)
            return flat_list

        def findMinMaxYCoordinates(elements: list) -> tuple:
            """
            Find the minimum y2 and maximum y1 coordinates from the list of elements.

            Args:
                elements (list): List of elements.

            Returns:
                tuple: Minimum y2 and maximum y1 values.
            """
            minimum_y2 = min(e.y2 for e in elements)
            maximum_y1 = max(e.y1 for e in elements)
            return minimum_y2, maximum_y1

        # Main logic
        elements_with_x1 = filterElementsByX1(page, x1_table)  # Filter elements by x1 coordinate
        first_element_with_x1, last_element_with_x1 = findBoundaryElements(elements_with_x1)  # Find boundary elements
        text_end_words = collectTextEndWords(page, first_element_with_x1, last_element_with_x1, x1_table, text_end_coord)  # Collect text end words

        table_row_elements = unit_elements + text_end_words  # Combine unit elements and text end words
        flat_list = flattenElementList(table_row_elements)  # Flatten the list of elements
        y1_table, y2_table = findMinMaxYCoordinates(flat_list)

        # Find and return the minimum y2 and maximum y1 values
        return y1_table, y2_table

    def determineTableX2(unit_elements: list) -> int:
        """
        Determine the maximum x2 value from unit elements.

        Args:
            unit_elements (list): List of unit elements to be considered.

        Returns:
            int: The maximum x2 value or -1 if no such value is found.
        """
        if not unit_elements:
            return -1

        maximum_x2 = max(te.x2 for te in unit_elements)
        return maximum_x2

    # Main Logic
    x1_table = determineTableX1(page)
    SaveImagesHandler.printAndSaveLinesList(page, [(x1_table, 0, x1_table, page.image.shape[0])], Constants.green, 2, Path.modified,
                                         "table_detection_x1")

    if x1_table != -1:
        text_end_coord, unit_start_coord, unit_elements = determineUnitSpace()
        lines = [
            (text_end_coord, 0, text_end_coord, page.image.shape[0]),
            (unit_start_coord, 0, unit_start_coord, page.image.shape[0])
        ]
        SaveImagesHandler.printAndSaveLinesList(page, lines, Constants.green, 2, Path.modified, "table_detection_unit_space")
        SaveImagesHandler.printAndSaveRectangleElements(page, unit_elements, Path.modified, "table_detection_unit_elements")

        y1_table, y2_table = determineTableY1Y2(page, x1_table, text_end_coord, unit_elements)
        x2_table = determineTableX2(unit_elements)

        margin = 2
        page.tables.append(Table(False, x1=x1_table-margin, y1=y1_table-margin, x2=x2_table+margin, y2=y2_table+margin))