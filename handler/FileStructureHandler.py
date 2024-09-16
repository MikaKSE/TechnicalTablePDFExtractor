# --// IMPORTS \\-- #
# -- Libraries -- #
from pathlib import Path


# --// PROGRAMM \\-- #
def deleteAllFilesInDir(path: str) -> None:
    for file in Path(path).iterdir():
        if file.is_file():
            file.unlink()


def createDirectory(path: str) -> None:
    Path(path).mkdir(parents=True, exist_ok=True)