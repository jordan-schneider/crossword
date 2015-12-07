"""Crossword Application Constants.

This module is not to be confused with the settings module, which
handles user-configurable options. Constants is instead a set of
options set by the developer.
"""

# Import
import os as _os
import logging

# File system reference
ROOT = _os.path.abspath(_os.path.dirname(__file__))
SETTINGS = "settings.xml"
PLAYERS = "players.json"
COPY = "default"

# Logging
FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATE = "%m/%d/%y %I:%M:%S %p"
logging.basicConfig(format=FORMAT, datefmt=DATE, level=logging.NOTSET)

# Alignment and spacing constants
FULL_PAD = 10
HALF_PAD = FULL_PAD // 2
TINY_PAD = FULL_PAD // 4
PAD = HALF_PAD
CANVAS_PAD_LEFT = 3
CANVAS_PAD = 4
NUMBER_PAD_LEFT = 2
NUMBER_PAD_TOP = 6
DEFAULT_PUZZLE_HEIGHT = 15
DEFAULT_PUZZLE_WIDTH = 15

# Control constants
ALL_ARROWS = ("Left", "Right", "Up", "Down")
ACROSS_ARROWS = ("Left", "Right")
DOWN_ARROWS = ("Up", "Down")
NEGATIVE_ARROWS = ("Left", "Up")
POSITIVE_ARROWS = ("Right", "Down")

# Model constants
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"

# Allowed colors
COLORS = ["red", "blue", "green"]

# Network events
CLIENT_JOINED = "client joined"
CLIENT_UPDATED = "client updated"
CLIENT_EXITED = "client exited"
CLIENT_KICKED = "server kicked"
SERVER_STOPPED = "server stopped"
SERVER_UPDATED = "server updated"
PUZZLE_REQUESTED = "puzzle requested"
PUZZLE_SUBMITTED = "puzzle submitted"
PUZZLE_PASSED = "puzzle passed"
PUZZLE_UPDATED = "puzzle updated"

POSITION = "position"
DIRECTION = "direction"
CLIENTS = "clients"
