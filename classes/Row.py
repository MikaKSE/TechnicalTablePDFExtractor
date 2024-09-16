# --// IMPORTS \\-- #
# -- Classes -- #
from classes.Element import Element


# --// PROGRAMM \\-- #
class Row:
    def __init__(self, row_nr: int, y):
        self.nr: int = row_nr
        self.elements: list[Element] = []
        self.y = y
        self.has_unit: bool = False


    def __str__(self):
        elements_text = ', '.join(e.text for e in self.elements)
        return f"Nr: {self.nr}, Has Unit: {self.has_unit}, Y: {self.y}, Elements: [{elements_text}]"