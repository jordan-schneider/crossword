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
NUMBER_LEFT = 6
NUMBER_TOP = 3

# Puzzle
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"

# Network
SERVER = "server"
CLIENT = "client"
PLAYER = "player"
SPECTATOR = "spectator"

