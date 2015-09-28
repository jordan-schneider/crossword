"""Crossword Application Constants.

This module is not to be confused with the `settings` module, which
handles user-configurable options. Constants is instead a set of
manually set options.
"""


# Import
import os
import platform


# Data
__author__ = "Noah Kim"
__version__ = "0.2.0"
__status__ = "Development"


# Convenience
def to_position(i: int, w: int) -> tuple:
    y, x = divmod(i, w)
    return x, y


def to_index(x: int, y: int, w: int) -> int:
    return y*w + x


# Settings
ROOT_DIRECTORY = os.path.abspath(os.path.dirname(__file__))
SETTINGS_PATH = os.path.join(ROOT_DIRECTORY, "settings.json")

# Padding
FULL_PAD = 10
HALF_PAD = FULL_PAD // 2
TINY_PAD = HALF_PAD // 2
PAD = HALF_PAD
CANVAS_SPARE = 2 + 2
CANVAS_PAD = 3

# Header view
SEPARATOR_HEIGHT = 1
SEPARATOR_COLOR = "black"

# Crossword view
DEFAULT_PUZZLE_WIDTH = 15
DEFAULT_PUZZLE_HEIGHT = 15

# Cell model
NUMBER_LEFT = 2
NUMBER_TOP = 6

# Puzzle
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"
ALL_ARROWS = ("Left", "Right", "Up", "Down")
ACROSS_ARROWS = ("Left", "Right")
DOWN_ARROWS = ("Up", "Down")
NEGATIVE_ARROWS = ("Left", "Up")
POSITIVE_ARROWS = ("Right", "Down")

# Network
SERVER = "server"
CLIENT = "client"
PLAYER = "player"
SPECTATOR = "spectator"

# Network messages
CLIENT_JOINED = "client joined"
CLIENT_EXITED = "client exited"
SERVER_STOPPED = "server stopped"
SERVER_KICKED = "server kicked"

PUZZLE_SUBMITTED = "puzzle submitted"
PUZZLE_REQUESTED = "puzzle requested"
PUZZLE_PASSED = "puzzle passed"

CLIENT_LIST = "client list"
ID_ASSIGNED = "id assigned"

CELL_SELECTED = "cell selected"
DIRECTION_SET = "direction set"
LETTER_INSERTED = "letter inserted"

# Network constants
DEFAULT_PORT = 50000

# Colors
COLORS = ["Red", "Orange", "Yellow", "Green", "Blue", "Purple"]

# Event bindings
if platform.system() == "Windows":
    BUTTON_2 = "<Button-3>"
else:
    BUTTON_2 = "<Button-2>"
