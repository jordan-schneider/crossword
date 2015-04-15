# Crossword
# Noah Kim

# Logging
import logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(format="%(levelname)8s %(asctime)s %(message)s", datefmt="%I:%M:%S %p", level=NOTSET)
logging.log(INFO, "logging started")

# Import
import json
import platform
import tkinter
import threading
import queue
import socket
import struct
import pickle
import string
import time
import datetime
import sys

import puz

# Constant
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"

# Configuration
file = open("config.json")
config = json.load(file)

# Generated configuration
DARWIN = platform.system() == "Darwin"  # Platform information
WINDOW_LINE_HEIGHT = 3  # Line that separates title/author from game
WINDOW_SPACE_HEIGHT = 5  # Space between line and game
CANVAS_OFFSET = 3  # Canvas draw offset to compensate for tkinter issues
CANVAS_SPARE = 4  # More compensation
CANVAS_PAD_NUMBER_LEFT = 3  # Cell number location
CANVAS_PAD_NUMBER_TOP = 6  # Cell number location
SYS_FONT_MODIFIER = -5 if DARWIN else 0  # Windows makes fonts larger
MODIFIERS = {1: "Shift"}  # Hot keys
LETTERS = list(string.ascii_lowercase)  # Valid letters

# Player data
PLAYER_DATA_TEMPLATE = {
    "name": "",
    "color": "",
    "letters-lifetime": 0,
    "chat-entries": 0,
    "chat-words": 0,
    "chat-letters": 0,
    "letters-correct": 0,
}

SERVER_DATA_TEMPLATE = {
    "puzzle-author": "",
    "puzzle-width": 0,
    "puzzle-height": 0,
    "puzzle-cells": 0,
    "puzzle-words": 0,
    "time-fill": 0,
    "time-finish": 0,
}

# Crossword models
def index_to_position(index, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return index % array_width, index // array_width

def position_to_index(x, y, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return x + y*array_width

class CrosswordCell:
    """Container class for a single crossword cell. This handles setting the fill, coloring the letter, and drawing
    rebus mode. It draws itself to the canvas given its top left coordinates. Cell number is drawn in the top left."""

    def __init__(self, canvas, type, color, fill, x, y, letters="", number=""):
        """Magic method to initialize a new crossword cell."""
        self.canvas = canvas  # Tkinter Canvas from the main application
        self.type = type  # Letter or number
        self.color = color  # Letter color
        self.fill = fill  # Cell background fill
        self.x = x  # Top left x
        self.y = y  # Top left y
        self.letters = letters  # Letter or letters in the cell (rebus mode)
        self.number = number  # Cell number

        self.rebus = len(self.letters)
        self.canvas_ids = [] # For efficiently tracking the drawings on the canvas

        if self.type == EMPTY: self.fill = config.FILL_EMPTY
        elif self.type != LETTER: self.type = LETTER  # There are only two types

    def draw_to_canvas(self):
        """Draw the cell, its fill, letter and color, and number to the canvas at the cell's position."""
        self.canvas.delete(*self.canvas_ids) # Clear all parts of the cell drawn on the canvas
        cell_position = (self.x, self.y, self.x+config.CELL_SIZE, self.y+config.CELL_SIZE)
        self.canvas.create_rectangle(*cell_position, fill=self.fill)

        if self.type == LETTER:
            text_position = (self.x+config.CANVAS_PAD_LETTER, self.y+config.CANVAS_PAD_LETTER)  # Find the center
            custom_font = (config.FONT_FAMILY, int(config.CELL_SIZE / (1.2 + 0.6*len(self.letters))))
            letter_id = self.canvas.create_text(*text_position, text=self.letters, font=custom_font, fill=self.color)
            self.canvas_ids.append(letter_id)

            if self.number:
                number_position = (self.x+config.CANVAS_PAD_NUMBER_LEFT, self.y+config.CANVAS_PAD_NUMBER_TOP)
                custom_font = (config.FONT_FAMILY, int(config.CELL_SIZE / 3.5))
                number_id = self.canvas.create_text(*number_position, text=self.number, font=custom_font, anchor="w")
                self.canvas_ids.append(number_id)

    def update_options(self, **options):
        """Update cell attributes and redraw it to the canvas."""
        self.__dict__.update(options)  # Vulnerable
        self.rebus = len(self.letters)
        self.draw_to_canvas()

class CrosswordWord:
    """Container class for a crossword word that holds cell and puzzle info references."""

    def __init__(self, cells, info, solution):
        """Initialize a new crossword word with its corresponding letter cells puzzle info."""
        self.cells = cells
        self.info = info
        self.solution = solution

    def update_options(self, **options):
        """Update the options of every cell in the word. This is simply a parent convenience method."""
        for cell in self.cells: cell.update_options(**options)

class CrosswordBoard:
    """Container class for an entire crossword board. Essentially serves as a second layer on top of the puzzle class.
    This is what the server keeps track of, and every time a client makes a change they send the fill of their board."""

    def __init__(self, puzzle):
        """Create a crossword given a puzzle object."""
        self.puzzle = puzzle

        self.cells = []
        self.across_words = []
        self.down_words = []
        self.current_cell = None
        self.current_word = None

        for y in range(self.puzzle.height):  # Fill the cells matrix with None as placeholders
            self.cells.append([])
            for x in range(self.puzzle.width):
                self.cells[y].append(None)

        self.paused = True

    def __repr__(self):
        """Magic method for string representation."""
        return "[%i] crossword board" % id(self)

    def __setitem__(self, position, value):
        """Magic method for coordinate based index setting."""
        self.cells[position[1]][position[0]] = value

    def __getitem__(self, position):
        """Magic method for coordinate based index getting."""
        return self.cells[position[1]][position[0]]

    def index(self, cell):
        """Get the coordinates of a cell if it exists in the crossword board."""
        return index_to_position(sum(self.cells, []).index(cell), self.puzzle.width)

    def generate_words(self):
        """Generates all of the words for the crossword board and puts them in two lists."""
        for info in self.puzzle.numbering.across:
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            cells = [(self[x+i, y]) for i in range(length)]
            solution = "".join([self.puzzle.solution[info["cell"] + i] for i in range(length)])
            self.across_words.append(CrosswordWord(cells, info, solution))
        for info in self.puzzle.numbering.down:
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            cells = [self[x, y+i] for i in range(length)]
            solution = "".join([self.puzzle.solution[info["cell"] + i] for i in range(length)])
            self.down_words.append(CrosswordWord(cells, info, solution))
        logging.log(DEBUG, "%s crossword words generated", repr(self))

    def set_selected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the direction) as selected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        else: words = self.down_words
        if self.current_word:  # Deselect old word
            self.current_word.update_options(fill=config.FILL_DESELECTED)
        for word in words:  # Select new word
            if origin in word.cells:  # Find the word
                word.update_options(fill=config.FILL_SELECTED_WORD)
                origin.update_options(fill=config.FILL_SELECTED_LETTER)
                self.current_cell = origin
                self.current_word = word

    def set_deselected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the direction) as deselected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        else: words = self.down_words
        for word in words:
            if origin in word.cells:
                word.update_options(fill=config.FILL_DESELECTED)

# Crossword utilities
def get_full_solution(puzzle):
    """Return the full solution as a list with rebus entries."""
    solution = list(puzzle.solution)
    rebus = puzzle.rebus()
    for index in rebus.get_rebus_squares():
        solution[index] = rebus.solutions[rebus.table[index] - 1]
    return solution

# Crossword player
class CrosswordPlayer: ...