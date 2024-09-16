# --// IMPORTS \\-- #
# -- Libraries -- #
from typing import Iterable
import pdfminer.high_level

# -- Classes -- #
from classes.Element import Element


# --// PROGRAMM \\-- #
class Miner:
    def __init__(self, path, page_numbers: list[int] = None, password: str = None) -> None:
        self.path: str = path
        self.page_numbers: list[int] = page_numbers
        self.password: str = password

        self.elements: list[list[Element]] = []

        pdfminer_pages: Iterable = pdfminer.high_level.extract_pages(self.path, password, page_numbers)
        self.extractElements(pdfminer_pages)


    def __str__(self):
        return (
            f'Path: {self.path}, Pages: {self.page_numbers}, Password: {self.password}'
        )


    def extractElements(self, pdfminer_pages: Iterable):
        for pdfminer_page in pdfminer_pages:
            elements_page = []
            self.extractElementsFromPage(pdfminer_page, elements_page)
            self.elements.append(elements_page)


    def extractElementsFromPage(self, element, elements_page: list[Element]) -> Element:
        text: str = getText(element)
        coords: list[int] = getCoords(element)
        name: str = getName(element)

        element_created = Element(text, coords, name)
        elements_page.append(element_created)

        if hasattr(element, '__iter__'):
            for sub_element in element:
                element_created.sub_elements.append(self.extractElementsFromPage(sub_element, elements_page))

        return element_created


    def getElements(self) -> list[list[Element]]:
        return self.elements


def getText(o) -> str | None:  # Get the text of the element
    if hasattr(o, 'get_text'):
        return o.get_text().strip()
    return None


def getCoords(o) -> list[int] | None:  # Get the coords of the element
    if hasattr(o, 'bbox'):
        return [int(round(coord, 0)) for coord in o.bbox]
    return None


def getName(o) -> str:  # Get the name (category) of the element
    return o.__class__.__name__