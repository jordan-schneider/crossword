# Crossword
# Noah Kim

# Import
import logging
import tkinter
import configparser
import time
import datetime
import string

import puz

# Logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(format="%(levelname)8s %(asctime)s %(message)s", datefmt="%I:%M:%S %p", level=NOTSET)
logging.log(INFO, "crossword: started")

# Constant
class config:
    CELL_SIZE = 40
    FONT_FAMILY = "tkDefaultFont"
    FONT_SIZE_MODIFIER = 0
    FONT_COLOR = "black"
    FILL_UNSELECTED = "white"
    FILL_SELECTED_WORD = "light blue"
    FILL_SELECTED_LETTER = "yellow"
    FILL_EMPTY = "black"
    ON_DOUBLE_ARROW_KEY = "stay in cell"  # ["stay in cell", "move in direction"]
    ON_SPACE_KEY = "clear and skip"  # ["clear and skip", "change direction"]
    ON_ENTER_KEY = "next word"  # ["next word"]
    ON_LAST_LETTER_GO_TO = "next word"  # ["next word", "first cell", "same cell"]

    WINDOW_TITLE = "NYTimes Crossword Puzzle"
    WINDOW_LINE_FILL = "grey70"
    WINDOW_LINE_HEIGHT = 3
    WINDOW_SPACE_HEIGHT = 5
    WINDOW_CLOCK = True
    WINDOW_CLOCK_COLOR = "grey70"
    CANVAS_OFFSET = 3
    CANVAS_SPARE = 2 + 1 # 2 for outline and 1 for spare right hand pixels
    CANVAS_PAD_LETTER = CELL_SIZE // 2
    CANVAS_PAD_NUMBER_LEFT = 3
    CANVAS_PAD_NUMBER_TOP = 6
    FONT_TITLE = (FONT_FAMILY, 30 + FONT_SIZE_MODIFIER)
    FONT_HEADER = (FONT_FAMILY, 25 + FONT_SIZE_MODIFIER)
    FONT_LABEL = (FONT_FAMILY, 20 + FONT_SIZE_MODIFIER)
    FONT_LIST = (FONT_FAMILY, 15 + FONT_SIZE_MODIFIER)
    FONT_LETTER = (FONT_FAMILY, int(CELL_SIZE / 1.8))
    FONT_NUMBER = (FONT_FAMILY, int(CELL_SIZE / 3.5))

TYPE_LETTER = "-"
TYPE_EMPTY = "."
DOWN = "down"
ACROSS = "across"

# Configurable
parser = configparser.ConfigParser()
parser.read("config.txt")
config.update({parser[section][0]: parser[section][1] for section in parser})

