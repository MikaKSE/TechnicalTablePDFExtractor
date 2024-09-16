# --// IMPORTS \\-- #
# -- Classes -- #
from classes.Table import Table


# --// PROGRAMM \\-- #
class Element:
    def __init__(self, text: str, original_coords: list[int], name: str):
        self.text: str = text
        self.original_coords: list[int] = original_coords
        self.name: str = name

        self.sub_elements: list[Element] = []

        # Coords - Correspond with the coords of the converted image from the pdf
        self.x1: int | None = None
        self.y1: int | None = None
        self.x2: int | None = None
        self.y2: int | None = None

        # Horizontal and vertical mid-line through the boxes
        self.h_mid: tuple[int, int, int, int] = []
        self.v_mid: tuple[int, int, int, int] = []

        self.in_table: bool = False
        self.row: int | None = None

        # Formatted Coords - Because of the new format after cropping and adding a border
        self.fx1: int | None = None
        self.fy1: int | None = None
        self.fx2: int | None = None
        self.fy2: int | None = None

        # Horizontal and vertical formatted mid-line through the boxes
        self.fh_mid: tuple[int, int, int, int] = []
        self.fv_mid: tuple[int, int, int, int] = []

        self.row: list[int] = []
        self.column: list[int] = []

        self.alignment: str | None = None


    def __str__(self):
        return (
            f'Name: {self.name}, Original Coords: {self.original_coords}, Text: {self.text}'
        )


    def createImageCoords(self, height_img: int, factor: int = 2.777) -> None:
        self.x1 = int(round(self.original_coords[0] * factor, 0))
        self.y1 = int(round(height_img - self.original_coords[1] * factor, 0))
        self.x2 = int(round(self.original_coords[2] * factor, 0))
        self.y2 = int(round(height_img - self.original_coords[3] * factor, 0))


    def createMidLines(self) -> None:
        y = int(round((self.y1 + self.y2) / 2, 0))
        self.h_mid = [self.x1, y, self.x2, y]

        x = int(round((self.x1 + self.x2) / 2, 0))
        self.v_mid = [x, self.y1, x, self.y2]


    def trimImageCoords(self) -> None:
        first_element_x1 = None
        last_element_x2 = None

        if self.sub_elements:
            for e in self.sub_elements:
                if e.text != "":
                    first_element_x1 = e.x1
                    break

            for e in reversed(self.sub_elements):
                if e.text != "":
                    last_element_x2 = e.x2
                    break

            if first_element_x1 is not None and last_element_x2 is not None:
                self.x1 = first_element_x1
                self.x2 = last_element_x2


    def createFormattedCoords(self, table: Table, border_size) -> None:
        self.fx1 = self.x1 - table.x1 + border_size
        self.fy1 = self.y1 - table.y1 + border_size
        self.fx2 = self.x2 - table.x1 + border_size
        self.fy2 = self.y2 - table.y1 + border_size

        y = int(round((self.fy1 + self.fy2) / 2, 0))
        self.fh_mid = [self.fx1, y, self.fx2, y]

        x = int(round((self.fx1 + self.fx2) / 2, 0))
        self.fv_mid = [x, self.fy1, x, self.fy2]