# --// IMPORTS \\-- #
# -- Classes -- #
from classes.Element import Element
from classes.Page import Page


# --// PROGRAMM \\-- #
def assignElementsToPage(page: Page, page_elements: list[Element]):
    page.all_elements = page_elements


def createImageCoords(page: Page):
    for element in page.all_elements:
        if element.original_coords is not None:
            element.createImageCoords(page.image.shape[0])


def filterRelevantElements(page: Page):
    for element in page.all_elements:
        if element.name == 'LTTextLineHorizontal' and element.text.strip() != "":
            page.relevant_elements.append(element)


def trimImageCoords(page: Page):
    for element in page.relevant_elements:
        element.trimImageCoords()


def createMidLines(page: Page):
    for element in page.relevant_elements:
        element.createMidLines()