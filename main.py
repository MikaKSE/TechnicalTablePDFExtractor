# --// IMPORTS \\-- #
# -- Libraries -- #
from pdf2image import convert_from_path
import cv2 as cv

# -- TypeCasting -- #
from PIL.Image import Image
from numpy import ndarray

# -- Handler -- #
from handler import FileStructureHandler
from handler import MinerElementHandler
from handler import SaveImagesHandler
from handler import TableDetectionHandler
from handler import ImageProcessHandler
from handler import ContourHandler
from handler import TableLinesHandler
from handler import TableAssignmentHandler
from handler import TableNoLinesHandler

# -- Classes -- #
from classes.Page import Page
from classes.Miner import Miner
import Path
import Constants

# --// PROGRAMM \\-- #
print("---< Programm Start >---")

# -- PATHS -- #
pdf: str = "TemplateWithoutLines"  # INPUT: PDF name

path_pdf: str = f'{Path.assets}/pdfs/{pdf}.pdf'

# -- CONVERT PDF TO IMAGES -- #
imgs_converted: list[Image] = convert_from_path(path_pdf)  # Convert the pdf with <pdf2image>

FileStructureHandler.createDirectory(Path.assets)
FileStructureHandler.createDirectory(Path.temp)
FileStructureHandler.createDirectory(Path.pages)
FileStructureHandler.createDirectory(Path.modified)
FileStructureHandler.createDirectory(Path.output)

FileStructureHandler.deleteAllFilesInDir(Path.pages)
FileStructureHandler.deleteAllFilesInDir(Path.modified)
FileStructureHandler.deleteAllFilesInDir(Path.output)

Miner = Miner(path_pdf)

pages: list[Page] = []
for page_number, img_converted in enumerate(imgs_converted):
    save_path: str = f'{Path.pages}/page_{page_number}.jpg'
    img_converted.save(save_path, 'JPEG')  # Save each image as page_{nr}
    img_cv_read: ndarray = cv.imread(save_path)
    pages.append(Page(page_number, img_cv_read))

for page in pages:
    # Prepare and generate needed coords
    MinerElementHandler.assignElementsToPage(page, Miner.elements[page.nr])
    MinerElementHandler.createImageCoords(page)
    SaveImagesHandler.printAndSaveRectangleElements(page, page.all_elements, Path.modified, 'elements_all')
    MinerElementHandler.filterRelevantElements(page)
    SaveImagesHandler.printAndSaveRectangleElements(page, page.relevant_elements, Path.modified, 'elements_relevant')
    MinerElementHandler.trimImageCoords(page)
    SaveImagesHandler.printAndSaveRectangleElements(page, page.relevant_elements, Path.modified, 'elements_trimmed')
    MinerElementHandler.createMidLines(page)
    SaveImagesHandler.printAndSaveSpecialBox(page, page.image, page.relevant_elements, Path.modified, 'elements_special_boxes')

    # Preprocess Images
    page.img_gray, page.img_thresh = ImageProcessHandler.createGrayAndThresh(page.image)
    SaveImagesHandler.saveImage(page, page.img_gray, Path.modified, 'gray')
    SaveImagesHandler.saveImage(page, page.img_thresh, Path.modified, 'thresh')

    # Detect contours
    contours, hierarchies = ImageProcessHandler.findContours(page.img_thresh)
    page.contours_all = ContourHandler.createContourObjects(contours, hierarchies)
    SaveImagesHandler.printAndSaveContourObjects(page, page.contours_all, Path.modified, 'contours_all')

    # Detect table with lines
    TableDetectionHandler.getTablesWithLines(page.contours_all[0], page)
    TableDetectionHandler.getTablesWithoutLines(page)

    page.tables.reverse()
    for i, table in enumerate(page.tables):
        table.nr = i
        table.setElements(page.relevant_elements)
        if table.has_lines:
            SaveImagesHandler.printAndSaveContourObjects(page, [table.contour], Path.modified, f'detected_table_{i}')
        SaveImagesHandler.printAndSaveSpecialBox(page, page.image, table.elements, Path.modified, f'detected_table_elements_{i}')

    # Detailed table with lines analysis
    for table in page.tables:
        # Preprocess Image
        TableLinesHandler.cropTable(page, table)
        SaveImagesHandler.saveImage(page, table.image, Path.modified, f'table_cropped_{table.nr}')
        table.img_border = ImageProcessHandler.addBorder(table.image, border_size=Constants.border_size)
        SaveImagesHandler.saveImage(page, table.img_border, Path.modified, f'table_bordered_{table.nr}')
        table.img_gray = ImageProcessHandler.makeImageGray(table.img_border)
        SaveImagesHandler.saveImage(page, table.img_gray, Path.modified, f'table_gray_{table.nr}')
        table.img_thresh = ImageProcessHandler.makeImageThresh(table.img_gray)
        SaveImagesHandler.saveImage(page, table.img_thresh, Path.modified, f'table_thresh_{table.nr}')
        # Assign Element
        TableAssignmentHandler.sortElements(table)
        TableAssignmentHandler.createFormattedElementCoords(table, Constants.border_size)
        SaveImagesHandler.printAndSaveFormattedSpecialBox(page, table.img_border, table.elements, Path.modified, f'table_elements{table.nr}')

        if table.has_lines:
            # Detect Lines
            table.x_lines = TableLinesHandler.detectXLines(table.img_thresh)
            SaveImagesHandler.printAndSaveLines(page, table, table.x_lines, Constants.green, 3, Path.modified, f'x_lines_{table.nr}')

            table.y_lines = TableLinesHandler.detectYLines(table.img_thresh)
            SaveImagesHandler.printAndSaveLines(page, table, table.y_lines, Constants.green, 3, Path.modified, f'y_lines_{table.nr}')

            table.dead_end_lines = TableLinesHandler.findLeftDeadEnds(table.x_lines, table.y_lines)
            table.dead_end_lines.extend(TableLinesHandler.findRightDeadEnds(table.x_lines, table.y_lines))
            SaveImagesHandler.printAndSaveLines(page, table, table.dead_end_lines, Constants.green, 3, Path.modified, f'dead_end_lines{table.nr}')
            table.dead_end_vertical_lines = TableLinesHandler.findDeadEndVerticalLines(table.x_lines, table.dead_end_lines)
            SaveImagesHandler.printAndSaveLines(page, table, table.dead_end_vertical_lines, Constants.green, 3, Path.modified, f'dead_end_vertical_lines{table.nr}')
            table.y_lines.extend(table.dead_end_vertical_lines)

            TableAssignmentHandler.assignElements(table)

        else:
            table.img_row_dilate = ImageProcessHandler.makeImageDilate(table.img_thresh, (3001, 1))
            SaveImagesHandler.saveImage(page, table.img_row_dilate, Path.modified, f"table_dilate_row_{table.nr}")
            table.img_col_dilate = ImageProcessHandler.makeImageDilate(table.img_thresh, (41, 300))
            SaveImagesHandler.saveImage(page, table.img_col_dilate, Path.modified, f"table_dilate_col_{table.nr}")
            table.x_boxes = TableNoLinesHandler.detect_dilate_boxes(table.img_row_dilate)
            SaveImagesHandler.printAndSaveRectangle(table.img_border, table.x_boxes, Constants.green, 2, Path.modified, f"{page.nr}_table_x_boxes_{table.nr}")
            table.y_boxes = TableNoLinesHandler.detect_dilate_boxes(table.img_col_dilate)
            SaveImagesHandler.printAndSaveRectangle(table.img_border, table.y_boxes, Constants.green, 2, Path.modified, f"{page.nr}_table_y_boxes_{table.nr}")
            TableNoLinesHandler.sortXBoxes(table)
            TableNoLinesHandler.determineRow(table)
            TableNoLinesHandler.sortYBoxes(table)
            TableNoLinesHandler.determineColumn(table)
            TableNoLinesHandler.checkAlignment(table)
            TableNoLinesHandler.rearrangeIndentedElements(table)

        # Output
        SaveImagesHandler.consoleOutputTable(table)
        SaveImagesHandler.excelOutputTable(table.elements, Path.output, f"{page.nr}_excel_{table.nr}")

print("---< Programm Ende >---")