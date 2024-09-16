# --// IMPORTS \\-- #
# -- Libraries -- #
from pathlib import Path

# --// PROGRAMM \\-- #
home: str = str(Path(__file__).parent)  # Set the path_home directory with <pathlib>
assets: str = f'{home}/assets'
temp: str = f'{assets}/temp'
pages: str = f'{temp}/pages'
modified = f'{temp}/pages_modified'
output: str = f'{home}/output'