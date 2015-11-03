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
WORD = "word"
NORMAL = "normal"
ABSOLUTE = "absolute"

# Configuration
file = open("settings.json")
config = json.load(file)

# Generated configuration
DARWIN = platform.system() == "Darwin"  # Platform information
WINDOW_LINE_HEIGHT = 3  # Line that separates title/author from game
WINDOW_SPACE_HEIGHT = 5  # Space between line and game
CANVAS_OFFSET = 3  # Canvas draw offset to compensate for tkinter issues
CANVAS_SPARE = 4  # More compensation
CANVAS_PAD_NUMBER_LEFT = 3  # Cell number location
CANVAS_PAD_NUMBER_TOP = 6  # Cell number location
FONT_MODIFIER = 0 if DARWIN else 5  # Windows makes fonts larger
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
def index_to_position(index, width):
    """Determine the cartesian coordinates of an index in an array.

    index - index in the array
    width - width of the array
    """
    return index % width, index // width


def position_to_index(x, y, width):
    """Determine the index in an array of cartesian coordinates.

    x - x position in cartesian
    y - y position in cartesian
    width - width of the array
    """
    return x + y*width


class CrosswordCell:
    """Container class for a single crossword cell.

    This handles setting the fill, coloring the letter, and drawing
    rebus mode. It draws itself to the canvas given its top left
    coordinates. Cell number is drawn in the top left."""

    def __init__(self, canvas, type, color, fill, x, y, letters="", number=""):
        """Initialize a new CrosswordCell.

        canvas - tkinter.Canvas object for the CrosswordCell to draw on
        type - LETTER or EMPTY
        color - color of the letter in the cell
        fill - background color of the cell
        x - x position of the top left corner of the cell
        y - y position of the top left corner of the cell
        letters - the letters in the cell (supports rebus mode)
        number - the number in the top right corner of the cell
        """
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

        if self.type == EMPTY: self.fill = config["board"]["empty-fill"]
        elif self.type != LETTER: self.type = LETTER  # There are only two types

    def draw(self):
        """Draw the cell, its fill, letter and color, and number.

        Draws to the canvas at the cell's position.
        """
        self.canvas.delete(*self.canvas_ids) # Clear all parts of the cell drawn on the canvas
        cell_position = (self.x, self.y, self.x+config["board"]["cell-size"],
                         self.y+config["board"]["cell-size"])
        self.canvas.create_rectangle(*cell_position, fill=self.fill)

        if self.type == LETTER:
            text_position = (self.x+config["board"]["cell-size"]//2, self.y+config["board"]["cell-size"]//2)
            custom_font = (config, int(config["board"]["cell-size"] / (1.2 + 0.6*len(self.letters))))
            letter_id = self.canvas.create_text(*text_position, text=self.letters, font=custom_font, fill=self.color)
            self.canvas_ids.append(letter_id)

            if self.number:
                number_position = (self.x+CANVAS_PAD_NUMBER_LEFT, self.y+CANVAS_PAD_NUMBER_TOP)
                custom_font = (config["board"]["font-family"], int(config["board"]["cell-size"] / 3.5))
                number_id = self.canvas.create_text(*number_position, text=self.number, font=custom_font, anchor="w")
                self.canvas_ids.append(number_id)

    def update(self, **options):
        """Update cell attributes and redraw it to the canvas.

        It is possible for this function to access non-graphical
        attributes of the CrosswordCell.
        """
        self.__dict__.update(options)  # Vulnerable
        self.rebus = len(self.letters)
        self.draw()


class CrosswordWord:
    """Container class for a crossword word.

    Holds cell and puzzle info references."""

    def __init__(self, cells, info, solution):
        """Initialize a new crossword word with its corresponding
        letter cells puzzle info.

        cells - list of cells that comprise the word
        info - word info from the puzzle word list
        solution - the correct word for this cell
        """
        self.cells = cells
        self.info = info
        self.solution = solution

    def update(self, **options):
        """Update the options of every cell in the word. This is simply
        a parent convenience method.

        This method is also plagued by the same problems of
        `CrosswordCell.update`.
        """
        for cell in self.cells:
            cell.update(**options)


class CrosswordBoard:
    """Container class for an entire crossword board

    Essentially serves as a second layer on top of the puzzle class.
    This is what the server keeps track of, and every time a client
    makes a change they send the fill of their board."""

    def __init__(self, puzzle):
        """Create a crossword given a puzzle object.

        puzzle - puz library puzzle object
        """
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
        """Get the string representation of the board."""
        return "[%i] crossword board" % id(self)

    def __setitem__(self, position, value):
        """Set the value at a position in the crossword board.

        position - (x, y) value based on the array position of the item
        value - value to put at (x, y)
        """
        self.cells[position[1]][position[0]] = value

    def __getitem__(self, position):
        """Get the value at a position in the crossword board.

        position - (x, y) value based on the array position of the item
        """
        return self.cells[position[1]][position[0]]

    def generate_words(self):
        """Generates all of the words for the crossword board.

        Puts them in two lists, across and down.
        """
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

    def index(self, cell):
        """Get the coordinates of a cell if it exists in the board.

        cell - CrosswordCell to search for
        """
        return index_to_position(sum(self.cells, []).index(cell), self.puzzle.width)

    def set_selected(self, x, y, direction):
        """Set the word at the position of the origin letter as selected.

        Also sets the rest of the word as selected.

        x - x position of the origin letter
        y - y position of the origin letter
        direction - direction of the word to be selected
        """
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        else: words = self.down_words
        if self.current_word:  # Deselect old word
            self.current_word.update(fill=config.FILL_DESELECTED)
        for word in words:  # Select new word
            if origin in word.cells:  # Find the word
                word.update(fill=config.FILL_SELECTED_WORD)
                origin.update(fill=config.FILL_SELECTED_LETTER)
                self.current_cell = origin
                self.current_word = word

    def set_deselected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the direction) as deselected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        else: words = self.down_words
        for word in words:
            if origin in word.cells:
                word.update(fill=config.FILL_DESELECTED)

# Crossword utilities
def get_full_solution(puzzle):
    """Return the full solution as a list with rebus entries."""
    solution = list(puzzle.solution)
    rebus = puzzle.rebus()
    for index in rebus.get_rebus_squares():
        solution[index] = rebus.solutions[rebus.table[index] - 1]
    return solution

# Crossword player
class CrosswordPlayer:
    """The client crossword player application. Handles nothing except for the crossword board."""

    def __init__(self, name, color):
        """Magic method to initialize a new crossword player."""
        self.color = color
        self.name = name
        self.epoch = 0
        self.state = {}
        self.paused = False

    def __repr__(self):
        """Magic method for string representation."""
        return "[%i] crossword player" % id(self)

    def build(self):
        """Build the graphical graphics, draws the crossword board, and populates the clue lists."""
        self.window = tkinter.Tk()
        self.window.title("Crossword")
        self.window.resizable(False, False)

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill="both", padx=5, pady=5)

        self.title = tkinter.Label(self.frame)
        self.title.config(font=config["window"]["title-font"])
        self.title.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.author = tkinter.Label(self.frame)
        self.author.config(font=config["window"]["title-font"])
        self.author.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.line = tkinter.Frame(self.frame)
        self.line.config(height=3, bg=config["window"]["line-fill"])
        self.line.grid(row=1, column=0, columnspan=2, padx=5, sticky="we")

        self.game = tkinter.Frame(self.frame)
        self.game.grid(row=3, column=0, pady=5)

        self.game_info = tkinter.Label(self.game)
        self.game_info.config(font=config["window"]["header-font"], anchor="w")
        self.game_info.grid(row=0, column=0, padx=4, sticky="we")

        self.game_clock = tkinter.Label(self.game)
        self.game_clock.config(font=config["window"]["header-font"], fg=config["window"]["clock-color"])
        self.game_clock.grid(row=0, column=0, padx=2, sticky="e")

        self.game_board = tkinter.Canvas(self.game)
        self.game_board.config(highlightthickness=0)
        self.game_board.grid(row=1, column=0, padx=5-CANVAS_OFFSET, sticky="nwe")

        self.game_menu = tkinter.Menu(self.game_board)
        self.game_menu.add_command(label="Check selected letter")
        self.game_menu.add_command(label="Check selected word")
        self.game_menu.add_command(label="Check board")

        self.clues = tkinter.Frame(self.frame)
        self.clues.grid(row=3, column=1, rowspan=2, sticky="ns")
        self.clues.rowconfigure(0, weight=1)
        self.clues.rowconfigure(1, weight=1)

        self.across = tkinter.Frame(self.clues)
        self.across.grid(row=0, column=0, padx=5, pady=7, sticky="ns")
        self.across.rowconfigure(1, weight=1)

        self.across_label = tkinter.Label(self.across)
        self.across_label.config(text="Across", anchor="w", font=config["window"]["label-font"])
        self.across_label.grid(row=0, column=0, sticky="w")

        self.across_list = tkinter.Listbox(self.across)
        self.across_list.config(
            width=35, font=config["window"]["list-font"], bd=0, selectborderwidth=0,
            selectbackground=config["board"]["selected-word-fill"])
        self.across_list.grid(row=1, column=0, sticky="ns")

        self.across_scrollbar = tkinter.Scrollbar(self.across)
        self.across_scrollbar.grid(row=1, column=1, sticky="ns")

        self.across_list.config(yscrollcommand=self.across_scrollbar.set)
        self.across_scrollbar.config(command=self.across_list.yview)

        self.down = tkinter.Frame(self.clues)
        self.down.grid(row=1, column=0, padx=5, pady=7, sticky="ns")
        self.down.rowconfigure(1, weight=1)

        self.down_label = tkinter.Label(self.down)
        self.down_label.config(text="Down", anchor="w", font=config["window"]["label-font"])
        self.down_label.grid(row=0, column=0, sticky="w")

        self.down_list = tkinter.Listbox(self.down)
        self.down_list.config(
            width=35, font=config["window"]["list-font"], bd=0, selectborderwidth=0,
            selectbackground=config["board"]["selected-word-fill"])
        self.down_list.grid(row=1, column=0, sticky="ns")

        self.down_scrollbar = tkinter.Scrollbar(self.down)
        self.down_scrollbar.grid(row=1, column=1, sticky="ns")

        self.down_list.config(yscrollcommand=self.down_scrollbar.set)
        self.down_scrollbar.config(command=self.down_list.yview)

        self.chat_frame = tkinter.Frame(self.frame)
        self.chat_frame.grid(row=0, column=2, rowspan=9, sticky="NS")
        self.chat_frame.rowconfigure(0, weight=1)

        self.chat_text = tkinter.Text(self.chat_frame)
        self.chat_text.config(width=30, relief="sunken", bd=1, font=config["window"]["chat-font"],
                              state="disabled")
        self.chat_text.grid(row=0, column=0, padx=5, pady=5, sticky="NS")

        self.chat_entry = tkinter.Entry(self.chat_frame)
        self.chat_entry.config(font=config["window"]["chat-font"], state="disabled")  # Not working
        self.chat_entry.grid(row=1, column=0, padx=6, pady=5, sticky="EW")

        logging.log(DEBUG, "%s created application widgets", repr(self))

        self.window.bind_all("<Key>", self.event_key)
        self.window.bind_all("<Tab>", self.event_tab_key)
        self.window.bind_all("<Shift-Tab>", self.event_shift_tab_key)
        self.game_board.bind("<Button-1>", self.event_game_board_button_1)
        self.game_board.bind("<Button-2>" if DARWIN else "<Button-3>", self.event_game_board_button_2)
        self.across_list.bind("<Button-1>", self.event_across_list_button_1)
        self.down_list.bind("<Button-1>", self.event_down_list_button_1)
        self.chat_entry.bind("<Return>", self.event_chat_entry_return)

        self.window.bind_all("<<update-selected-clue>>", self.event_update_selected_clue)
        self.window.bind_all("<<update-game-info>>", self.event_update_game_info)
        self.window.bind_all("<<update-clock>>", self.event_update_clock)

        self.window.bind_all("<<event-tab-key-override>>", self.event_tab_key_override)
        self.window.bind_all("<<event-shift-tab-key-override>>", self.event_shift_tab_key_override)
        self.window.bind_all("<Escape>", self.event_escape_key)

        self.window.protocol('WM_DELETE_WINDOW', self.stop)

        logging.log(DEBUG, "%s bound events", repr(self))

        logging.log(DEBUG, "%s built the application", repr(self))

    def start(self):
        self.window.mainloop()

    def load_puzzle(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)
        self.puzzle.fill = list(self.puzzle.fill)
        self.puzzle.numbering = self.puzzle.clue_numbering()

        self.title.config(text=self.puzzle.title.lstrip("NY Times, "))
        self.author.config(text=self.puzzle.author)
        self.game_board.config(width=config["board"]["cell-size"]*self.puzzle.width + CANVAS_SPARE,
                               height=config["board"]["cell-size"]*self.puzzle.height + CANVAS_SPARE)

        self.game_board.create_rectangle(
            CANVAS_OFFSET, CANVAS_OFFSET,
            config["board"]["cell-size"]*self.puzzle.width + CANVAS_OFFSET,
            config["board"]["cell-size"]*self.puzzle.height + CANVAS_OFFSET)

        for clue in self.puzzle.numbering.across: clue.update({"dir": ACROSS})
        for clue in self.puzzle.numbering.down: clue.update({"dir": DOWN})
        self.board = CrosswordBoard(self.puzzle)

        numbers = {w["cell"]: w["num"] for w in self.puzzle.numbering.across}
        numbers.update({w["cell"]: w["num"] for w in self.puzzle.numbering.down})
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = CrosswordCell(
                    self.game_board, self.puzzle.fill[position_to_index(x, y, self.puzzle.width)],
                    "black", config["board"]["deselected-fill"], CANVAS_OFFSET + x*config["board"]["cell-size"],
                    CANVAS_OFFSET + y*config["board"]["cell-size"], number=numbers.get(y*self.puzzle.height + x, ""))
                self.board[x, y] = cell
                cell.draw()
        self.board.generate_words()
        logging.log(DEBUG, "%s populated crossword cells", repr(self))
        logging.log(DEBUG, "%s drew crossword puzzle", repr(self))

        logging.log(DEBUG, "%s loaded puzzle", repr(self))

        self.epoch = 0
        logging.log(DEBUG, "%s reset epoch", repr(self))
        self.pause()

    def move_current_cell(self, direction, distance, mode=NORMAL):
        x, y = self.board.index(self.board.current_cell)
        s = -1 if distance < 0 else 1
        self.board.set_selected(self, x, y, direction)
        self.direction = direction
        if direction == ACROSS:
            i = 0
            while i != distance:
                if x + s >= self.puzzle.width or x + s < 0: at_word_end = True
                elif self.board[x+s, y] not in self.board.current_word.cells: at_word_end = True
                else: at_word_end = False

                if mode == WORD or at_word_end and mode == NORMAL:
                    cell_info_index = self.puzzle.across.index(self.board.current_word.info)
                    next_cell_info = self.puzzle.across[(cell_info_index + s) % len(self.puzzle.across)]
                    next_cell_number = next_cell_info["cell"]
                    x, y = index_to_position(next_cell_info, self.puzzle.width)
                    self.board.current_word.update_options(fill=config["board"]["deselected-fill"])
                    if s == -1: x += next_cell_info["len"] - 1
                    self.board.set_selected(x, y, self.direction)
                elif at_word_end and mode == NORMAL:
                    if config["controls"]["on-last-letter-go-to"][0] == "first cell":
                        x -= self.board.current_word.info["len"] - 1
                    elif config["controls"]["on-last-letter-go-to"][0] == "same cell":
                        return
                elif mode == ABSOLUTE:
                    while self.board[x, y].type == EMPTY:
                        x = (x + s) % self.puzzle.width
                else:
                    x += s
                if config["controls"]["on-filled-letter"][0] == "skip" and mode == NORMAL and self.board[x, y].letters:
                    distance += s
                i += s
            self.board.set_selected(x, y, self.direction)
        elif direction == DOWN:
            i = 0
            while i != distance:
                if y + s >= self.puzzle.height or y + s < 0: at_word_end = True
                elif self.board[x, y+s] not in self.board.current_word.cells: at_word_end = True
                else: at_word_end = False

                if mode == WORD or at_word_end and mode == NORMAL:
                    cell_info_index = self.puzzle.down.index(self.board.current_word.info)
                    next_cell_info = self.puzzle.down[(cell_info_index + s) % len(self.puzzle.down)]
                    next_cell_number = next_cell_info["cell"]
                    x, y = index_to_position(next_cell_info, self.puzzle.width)
                    self.board.current_word.update_options(fill=config["board"]["deselected-fill"])
                    if s == -1: y += next_cell_info["len"] - 1
                    self.board.set_selected(x, y, self.direction)
                elif at_word_end and mode == NORMAL:
                    if config["controls"]["on-last-letter-go-to"][0] == "first cell":
                        y -= self.board.current_word.info["len"] - 1
                    elif config["controls"]["on-last-letter-go-to"][0] == "same cell":
                        return
                elif mode == ABSOLUTE:
                    while self.board[x, y].type == EMPTY:
                        y = (y + s) % self.puzzle.width
                else:
                    y += s
                if config["controls"]["on-filled-letter"][0] == "skip" and mode == NORMAL and self.board[x, y].letters:
                    distance += s
                i += s
            self.board.set_selected(x, y, self.direction)

    def get_selected_clue(self):
        selection = self.across_list.curselection()
        if selection: return self.numbering.across[int(selection[0])]
        selection = self.down_list.curselection()
        if selection: return self.numbering.down[int(selection[0])]

    def has_focus(self, widget): pass
    def write_cell(self, cell, letters): pass

    def event_update_selected_clue(self, event): pass
    def event_update_game_info(self, event): pass
    def event_update_clock(self, event): pass

    def event_key(self, event): pass
    def event_tab_key(self, event): pass
    def event_shift_tab_key(self, event): pass
    def event_tab_key_override(self, event): pass
    def event_shift_tab_key_override(self, event): pass
    def event_chat_entry_return(self, event): pass
    def event_escape_key(self, event): pass

    def event_game_board_button_1(self, event): pass
    def event_game_board_button_2(self, event): pass
    def event_across_list_button_1(self, event): pass
    def event_down_list_button_1(self, event): pass

    def pause(self):
        self.game_board.delete("all")
        self.game_board.create_text(int(self.game_board.cget("width"))//2, int(self.game_board.cget("height"))//2,
                                    text="Paused", font=config.FONT_HEADER)

        self.state["time"] = time.time()
        self.state["chat"] = self.chat_text.get("1.0", "end-1c")
        self.state["cell"] = self.board.current_cell

        self.chat_text.delete("1.0", "end")
        self.chat_text.config(state="disabled")
        self.chat_entry.config(state="disabled")
        self.across_list.delete("0", "end")
        self.down_list.delete("0", "end")

        self.paused = True

    def play(self):
        for info in self.puzzle.numbering.across: self.across_list.insert("end", " %(num)i. %(clue)s" % info)
        for info in self.puzzle.numbering.down: self.down_list.insert("end", " %(num)i. %(clue)s" % info)
        logging.log(DEBUG, "%s populated clue lists", repr(self))

        self.window.event_generate("<<update-game-info>>")
        self.window.event_generate("<<update-clock>>")
        logging.log(DEBUG, "%s triggered update events", repr(self))

        self.epoch = time.time()

player = CrosswordPlayer("Noah", "black")
player.build()
player.load_puzzle("puzzles/Nov0705.puz")
player.start()
