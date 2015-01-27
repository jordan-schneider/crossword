# Crossword
# Noah Kim


# Import
import logging
import tkinter
import time
import datetime
import platform
import string
import pickle
import threading
import queue
import socket
import struct
import sys

import puz


# Logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(format="%(levelname)8s %(asctime)s %(message)s", datefmt="%I:%M:%S %p", level=NOTSET)
logging.log(INFO, "logging started")


# Constant
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"

WINDOWS_FONT_MODIFIER = -5
MAC_FONT_MODIFIER = 0
SELECTED_FONT_MODIFIER = MAC_FONT_MODIFIER if platform.system() == "Darwin" else WINDOWS_FONT_MODIFIER


# Configuration
def get_any_value(string):
    """Get any possible values out of a string. This is a cheap method and is probably unstable. Just a workaround for
    the namespace configuration file reader."""
    try: return eval(string, {}, {})
    except: return string

class Config:
    """The configuration namespace. This is a container for all of the configurable and non-configurable options for the
    crossword app. It also has a method that reads from and dump to a configuration file, but this is only used for
    initial configuration and changes made by the user in the settings menu."""

    CELL_SIZE = 33
    FONT_FAMILY = "tkDefaultFont"
    FONT_SIZE_MODIFIER = 0
    FONT_COLOR = "black"
    FILL_DESELECTED = "white"
    FILL_SELECTED_WORD = "light blue"
    FILL_SELECTED_LETTER = "yellow"
    FILL_EMPTY = "black"
    FILL_CORRECT = "green"
    FILL_INCORRECT = "red"
    ON_DOUBLE_ARROW_KEY = "stay in cell"  # ["stay in cell", "move in direction"]
    ON_SPACE_KEY = "clear and skip"  # ["clear and skip", "change direction"]
    #ON_ENTER_KEY = "next word"  # ["next word"]
    #ON_TAB_KEY = "next word"  # ["next word"]
    ON_LAST_LETTER_GO_TO = "next word"  # ["next word", "first cell", "same cell"]

    WINDOW_TITLE = "NYTimes Crossword Puzzle"
    WINDOW_LINE_FILL = "grey70"
    WINDOW_LINE_HEIGHT = 3
    WINDOW_SPACE_HEIGHT = 5
    WINDOW_CLOCK = True
    WINDOW_CLOCK_COLOR = "grey70"
    CANVAS_OFFSET = 3
    CANVAS_SPARE = 2 + 2  # 2 for outline and 1 for spare right hand pixels

    @property  # These values are calculated on the fly
    def CANVAS_PAD_LETTER(self):
        return self.CELL_SIZE // 2 + 1

    CANVAS_PAD_NUMBER_LEFT = 3
    CANVAS_PAD_NUMBER_TOP = 6

    @property
    def FONT_TITLE(self):
        return self.FONT_FAMILY, 25 + self.FONT_SIZE_MODIFIER

    @property
    def FONT_HEADER(self):
        return self.FONT_FAMILY, 20 + self.FONT_SIZE_MODIFIER

    @property
    def FONT_LABEL(self):
        return self.FONT_FAMILY, 15 + self.FONT_SIZE_MODIFIER

    @property
    def FONT_LIST(self):
        return self.FONT_FAMILY, 10 + self.FONT_SIZE_MODIFIER

    @property
    def FONT_CHAT(self):
        return self.FONT_FAMILY, 0

    FILE_CONFIG = "config.txt"  # Very meta (._.)

    def __init__(self):
        """Magic method for initialization."""
        self.read_file_options = []

    def read_file(self, file_path):
        """Reads the configurations from the file at file_path and updates the namespace's nickname with them. Also
        records what items were read from the file so that the same ones can be dumped in dump_file."""
        self.read_file_options = []
        with open(file_path) as file:
            for line in file.read().split("\n"):
                option, value = map(lambda item: item.strip(), line.split(":"))
                setattr(self, option, get_any_value(value))
                self.read_file_options.append(option)

    def dump_file(self, file_path, dump_all=False):
        """Dumps the configurations from the namespace to file_path. This method ONLY dumps the methods read in
        read_file unless dump_all is set to True."""
        with open(file_path, "w") as file:
            file.write("\n".join(["%s: %s" % (option, getattr(self, option)) for option in self.read_file_options]))

config = Config()
config.read_file(config.FILE_CONFIG)
logging.log(DEBUG, "config namespace loaded")


# Crossword Models
def index_to_position(index, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return index % array_width, index // array_width

def position_to_index(x, y, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return x + y*array_width

class Cell:
    """Container class for a single crossword cell. This handles setting the fill, coloring the letter, and drawing
    rebus mode. It draws itself to the canvas given its top left coordinates. Cell number is drawn in the top left."""

    def __init__(self, canvas, type, color, fill, x, y, letters="", number=""):
        """Magic method to initialize a new crossword cell."""
        self.canvas = canvas # Tkinter Canvas from the main application
        self.type = type # Letter or number
        self.color = color # Letter color
        self.fill = fill # Cell background fill
        self.x = x # Top left x
        self.y = y # Top left y
        self.letters = letters # Letter or letters in the cell (rebus mode)
        self.number = number # Cell number

        self.rebus = len(self.letters)
        self.canvas_ids = [] # For efficiently tracking the drawings on the canvas

        if self.type == EMPTY:
            self.fill = config.FILL_EMPTY
        elif self.type != LETTER:
            self.letters = self.type  # This worked out really well
            self.type = LETTER

    def draw_to_canvas(self):
        """Draw the cell, its fill, letter and color, and number to the canvas at the cell's position."""
        self.canvas.delete(*self.canvas_ids) # Clear all parts of the cell drawn on the canvas
        cell_position = (self.x, self.y, self.x+config.CELL_SIZE, self.y+config.CELL_SIZE)
        cell_id = self.canvas.create_rectangle(*cell_position, fill=self.fill)

        if self.type == LETTER:
            text_position = (self.x+config.CANVAS_PAD_LETTER, self.y+config.CANVAS_PAD_LETTER) # Find the center
            custom_font = (config.FONT_FAMILY, int(config.CELL_SIZE / (1.2 + 0.6*len(self.letters))))
            # Devised the 1.2 + 0.6*len(...) based on observation
            letter_id = self.canvas.create_text(*text_position, text=self.letters, font=custom_font, fill=self.color)
            self.canvas_ids.append(letter_id)

            if self.number:
                number_position = (self.x+config.CANVAS_PAD_NUMBER_LEFT, self.y+config.CANVAS_PAD_NUMBER_TOP)
                custom_font = (config.FONT_FAMILY, int(config.CELL_SIZE / 3.5)) # Another arbitrary measurement
                number_id = self.canvas.create_text(*number_position, text=self.number, font=custom_font, anchor="w")
                self.canvas_ids.append(number_id)

    def update_options(self, **options):
        """Update cell attributes and redraw it to the canvas."""
        self.__dict__.update(options)
        self.rebus = len(self.letters)
        self.draw_to_canvas()

class Word:
    """Container class for a crossword word that holds cell and puzzle info references. This is a convenience class.
    Some of it is a bit sloppy as well and the general algorithm should be reconsidered eventually."""

    def __init__(self, cells, info, solution):
        """Initialize a new crossword word with its corresponding letter cells puzzle info."""
        self.cells = cells
        self.info = info
        self.solution = solution

    def update_options(self, **options):
        """Update the options of every cell in the word. This is simply a parent convenience method."""
        for cell in self.cells: cell.update_options(**options)

class Board:
    """Container class for an entire crossword board. Essentially serves as a second layer on top of the puzzle class.
    This is what the server keeps track of, and every time a client makes a change they send the fill of their board."""

    def __init__(self, puzzle, numbering):
        """Create a crossword given a puzzle object."""
        self.puzzle = puzzle
        self.numbering = numbering

        self.cells = []
        self.across_words = []
        self.down_words = []
        self.current_cell = None
        self.current_word = None

        for y in range(self.puzzle.height):  # Fill the cells matrix with None as placeholders
            self.cells.append([])
            for x in range(self.puzzle.width):
                self.cells[y].append(None)

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
        for info in self.numbering.across:
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            cells = [(self[x+i, y]) for i in range(length)]
            solution = "".join([self.puzzle.solution[info["cell"] + i] for i in range(length)])
            self.across_words.append(Word(cells, info, solution))
        for info in self.numbering.down:
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            cells = [self[x, y+i] for i in range(length)]
            solution = "".join([self.puzzle.solution[info["cell"] + i] for i in range(length)])
            self.down_words.append(Word(cells, info, solution))
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


# Application Classes
MODIFIERS = {1: "Shift"}
LETTERS = list(string.ascii_lowercase)

def is_chat_string_allowed(string):
    print(string)
    for character in string:
        if character not in list(string.printable):
            return False
    return True

class Player:
    """The bare client crossword player. Handles nothing except for the crossword board."""

    def __init__(self, name, color):
        """Magic method to initialize a new crossword player."""
        self.color = color
        self.name = name

    def __repr__(self):
        """Magic method for string representation."""
        return "[%i] crossword player" % id(self)

    def load_puzzle(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)                                                                        # puz.read
        self.puzzle.fill = list(self.puzzle.fill)

        self.numbering = self.puzzle.clue_numbering()
        for clue in self.numbering.across: clue.update({"dir": ACROSS})
        for clue in self.numbering.down: clue.update({"dir": DOWN})
        self.board = Board(self.puzzle, self.numbering)
        logging.log(DEBUG, "%s loaded puzzle", repr(self))

    def build_application(self):
        """Build the graphical interface, draws the crossword board, and populates the clue lists."""
        self.window = tkinter.Tk()
        self.window.title(config.WINDOW_TITLE)
        self.window.resizable(False, False)

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill="both", padx=5, pady=5)

        self.title = tkinter.Label(self.frame)
        self.title.config(text=self.puzzle.title[10:], font=config.FONT_TITLE)
        self.title.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.author = tkinter.Label(self.frame)
        self.author.config(text=self.puzzle.author, font=config.FONT_TITLE)
        self.author.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.line = tkinter.Frame(self.frame)
        self.line.config(height=config.WINDOW_LINE_HEIGHT, bg=config.WINDOW_LINE_FILL)
        self.line.grid(row=1, column=0, columnspan=2, padx=5, sticky="we")

        self.space = tkinter.Frame(self.frame)
        self.space.config(height=config.WINDOW_SPACE_HEIGHT)
        self.space.grid(row=2, column=0, columnspan=2, padx=8, sticky="we")

        self.game = tkinter.Frame(self.frame)
        self.game.grid(row=3, column=0)

        self.game_info = tkinter.Label(self.game)
        self.game_info.config(font=config.FONT_HEADER, anchor="w")
        self.game_info.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.game_clock = tkinter.Label(self.game)
        self.game_clock.config(font=config.FONT_HEADER, fg=config.WINDOW_CLOCK_COLOR)
        if config.WINDOW_CLOCK: self.game_clock.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.game_board = tkinter.Canvas(self.game)
        self.game_board.config(
            width=config.CELL_SIZE*self.puzzle.width + config.CANVAS_SPARE,
            height=config.CELL_SIZE*self.puzzle.height + config.CANVAS_SPARE,
            highlightthickness=0)
        self.game_board.grid(row=1, column=0, padx=5-config.CANVAS_OFFSET, pady=5, sticky="nwe")

        self.game_menu = tkinter.Menu(self.game_board)
        self.game_menu.add_command(label="Check selected letter")
        self.game_menu.add_command(label="Check selected word")
        self.game_menu.add_command(label="Check board")

        self.clues = tkinter.Frame(self.frame)
        self.clues.grid(row=3, column=1, rowspan=2, sticky="ns")
        self.clues.rowconfigure(0, weight=1)
        self.clues.rowconfigure(1, weight=1)

        self.across = tkinter.Frame(self.clues)
        self.across.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        self.across.rowconfigure(1, weight=1)

        self.across_label = tkinter.Label(self.across)
        self.across_label.config(text="Across", anchor="w", font=config.FONT_LABEL)
        self.across_label.grid(row=0, column=0, sticky="w")

        self.across_list = tkinter.Listbox(self.across)
        self.across_list.config(
            width=35, font=config.FONT_LIST, bd=0, selectborderwidth=0, selectbackground=config.FILL_SELECTED_WORD)
        self.across_list.grid(row=1, column=0, sticky="ns")

        self.across_scrollbar = tkinter.Scrollbar(self.across)
        self.across_scrollbar.grid(row=1, column=1, sticky="ns")

        self.across_list.config(yscrollcommand=self.across_scrollbar.set)
        self.across_scrollbar.config(command=self.across_list.yview)

        self.down = tkinter.Frame(self.clues)
        self.down.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        self.down.rowconfigure(1, weight=1)

        self.down_label = tkinter.Label(self.down)
        self.down_label.config(text="Down", anchor="w", font=config.FONT_LABEL)
        self.down_label.grid(row=0, column=0, sticky="w")

        self.down_list = tkinter.Listbox(self.down)
        self.down_list.config(
            width=35, font=config.FONT_LIST, bd=0, selectborderwidth=0, selectbackground=config.FILL_SELECTED_WORD)
        self.down_list.grid(row=1, column=0, sticky="ns")

        self.down_scrollbar = tkinter.Scrollbar(self.down)
        self.down_scrollbar.grid(row=1, column=1, sticky="ns")

        self.down_list.config(yscrollcommand=self.down_scrollbar.set)
        self.down_scrollbar.config(command=self.down_list.yview)

        self.chat_frame = tkinter.Frame(self.frame)
        self.chat_frame.grid(row=0, column=2, rowspan=9, sticky="NS")
        self.chat_frame.rowconfigure(0, weight=1)

        self.chat_text = tkinter.Text(self.chat_frame)
        self.chat_text.config(width=30, relief="sunken", bd=1, font=config.FONT_CHAT, state="disabled")
        self.chat_text.grid(row=0, column=0, padx=5, pady=5, sticky="NS")

        self.chat_entry = tkinter.Entry(self.chat_frame)
        self.chat_entry.config(font=config.FONT_CHAT, validatecommand=(is_chat_string_allowed, "%S"))  # Not working
        self.chat_entry.grid(row=1, column=0, padx=6, pady=5, sticky="EW")

        logging.log(DEBUG, "%s created application widgets", repr(self))

        self.window.bind_all("<Key>", self.event_key)
        self.window.bind_all("<Tab>", self.event_tab_key)
        self.window.bind_all("<Shift-Tab>", self.event_shift_tab_key)
        self.game_board.bind("<Button-1>", self.event_game_board_button_1)
        button_2 = "<Button-2>" if platform.system() == "Darwin" else "<Button-3>"
        self.game_board.bind(button_2, self.event_game_board_button_2)
        self.across_list.bind("<Button-1>", self.event_across_list_button_1)
        self.down_list.bind("<Button-1>", self.event_down_list_button_1)
        self.chat_entry.bind("<Return>", self.event_chat_entry_return)

        self.window.bind_all("<<update-selected-clue>>", self.event_update_selected_clue)
        self.window.bind_all("<<update-game-info>>", self.event_update_game_info)
        self.window.bind_all("<<update-clock>>", self.event_update_clock)

        self.window.bind_all("<<event-tab-key-override>>", self.event_tab_key_override)
        self.window.bind_all("<<event-shift-tab-key-override>>", self.event_shift_tab_key_override)

        self.window.protocol('WM_DELETE_WINDOW', self.stop)

        logging.log(DEBUG, "%s bound events", repr(self))

        self.game_board.create_rectangle(
            config.CANVAS_OFFSET, config.CANVAS_OFFSET,
            config.CELL_SIZE*self.puzzle.width + config.CANVAS_OFFSET,
            config.CELL_SIZE*self.puzzle.height + config.CANVAS_OFFSET)

        numbers = {w["cell"]: w["num"] for w in self.numbering.across}
        numbers.update({w["cell"]: w["num"] for w in self.numbering.down})
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = Cell(
                    self.game_board, self.puzzle.fill[position_to_index(x, y, self.puzzle.width)], config.FONT_COLOR,
                    config.FILL_DESELECTED, config.CANVAS_OFFSET + x*config.CELL_SIZE,
                    config.CANVAS_OFFSET + y*config.CELL_SIZE, number=numbers.get(y*self.puzzle.height + x, ""))
                self.board[x, y] = cell
                cell.draw_to_canvas()
        self.board.generate_words()
        logging.log(DEBUG, "%s populated crossword cells", repr(self))
        logging.log(DEBUG, "%s drew crossword puzzle", repr(self))

        for info in self.numbering.across: self.across_list.insert("end", " %(num)i. %(clue)s" % info)
        for info in self.numbering.down: self.down_list.insert("end", " %(num)i. %(clue)s" % info)
        self.across_list.selection_set(0)
        logging.log(DEBUG, "%s populated clue lists", repr(self))

        self.direction = "across"
        self.board.set_selected(0, 0, self.direction)
        logging.log(DEBUG, "%s built the application", repr(self))

    def move_current_selection(self, direction, distance, force_next_word=False):
        """Move the current selection by the distance in the specified direction."""
        x, y = self.board.index(self.board.current_cell)
        s = -1 if distance < 0 else 1
        self.board.set_selected(x, y, direction)
        self.direction = direction
        if direction == ACROSS:
            for i in range(0, distance, s):
                if x + s >= self.puzzle.width or x + s < 0: at_word_end = True
                elif self.board[x+s, y] not in self.board.current_word.cells: at_word_end = True
                else: at_word_end = False
                if at_word_end:
                    if config.ON_LAST_LETTER_GO_TO == "first cell" and not force_next_word:
                        x -= self.board.current_word.info["len"] - 1
                    elif config.ON_LAST_LETTER_GO_TO == "same cell" and not force_next_word:
                        return
                    else:
                        cell_info_index = self.numbering.across.index(self.board.current_word.info)
                        next_cell_info = self.numbering.across[(cell_info_index + s) % len(self.numbering.across)]
                        next_cell_number = next_cell_info["cell"]
                        x, y = index_to_position(next_cell_number, self.puzzle.width)
                        self.board.current_word.update_options(fill=config.FILL_DESELECTED)
                        if s == -1: x += next_cell_info["len"] - 1
                        self.board.set_selected(x, y, self.direction)
                else:
                    x += s
            self.board.set_selected(x, y, self.direction)
        elif direction == DOWN:
            for i in range(0, distance, s):
                if y + s >= self.puzzle.height or y + s < 0: at_word_end = True
                elif self.board[x, y+s] not in self.board.current_word.cells: at_word_end = True
                else: at_word_end = False
                if at_word_end:
                    if config.ON_LAST_LETTER_GO_TO == "first cell" and not force_next_word:
                        y -= self.board.current_word.info["len"] - 1
                    elif config.ON_LAST_LETTER_GO_TO == "same cell" and not force_next_word:
                        return
                    else:
                        cell_info_index = self.numbering.down.index(self.board.current_word.info)
                        next_cell_info = self.numbering.down[(cell_info_index + s) % len(self.numbering.down)]
                        next_cell_number = next_cell_info["cell"]
                        x, y = index_to_position(next_cell_number, self.puzzle.width)
                        self.board.current_word.update_options(fill=config.FILL_DESELECTED)
                        if s == -1: y += next_cell_info["len"] - 1
                        self.board.set_selected(x, y, self.direction)
                else:
                    y += s
            self.board.set_selected(x, y, self.direction)

    def get_selected_clue(self):
        """Get which clue in the clue lists is selected."""
        selection = self.across_list.curselection()
        if selection: return self.numbering.across[int(selection[0])]
        selection = self.down_list.curselection()
        if selection: return self.numbering.down[int(selection[0])]

    def has_focus(self, widget):
        """Check if the chat entry has focus."""
        return str(self.window.focus_get()).endswith(str(id(widget)))

    def write_cell(self, cell, letters):
        """External method for inserting letters into cells. Needs to be here so that the multiplayer version can
        overwrite and use this to send data to the server."""
        cell.update_options(letters=letters, color=self.color)

    def event_update_selected_clue(self, event):
        """Update the selected clue."""
        word = self.board.current_word
        if word.info["dir"] == ACROSS:
            self.across_list.selection_clear(0, "end")
            self.across_list.selection_set(self.numbering.across.index(word.info))
            self.across_list.see(self.numbering.across.index(word.info))
        else:
           self.down_list.selection_clear(0, "end")
           self.down_list.selection_set(self.numbering.down.index(word.info))
           self.down_list.see(self.numbering.down.index(word.info))

    def event_update_game_info(self, event):
        """Update the current game info."""
        if self.get_selected_clue() is None:
            self.window.event_generate("<<update-selected-clue>>")
        clue = self.get_selected_clue().copy()
        clue["dir"] = clue["dir"][0].capitalize()
        self.game_info.config(text="%(num)i%(dir)s. %(clue)s" % clue)
        self.window.after(100, self.window.event_generate, "<<update-game-info>>")

    def event_update_clock(self, event):
        """Update the game time."""
        seconds = time.time() - self.epoch
        clock_time = str(datetime.timedelta(seconds=int(seconds)))
        self.game_clock.config(text=clock_time)
        self.window.after(100, self.window.event_generate, "<<update-clock>>")

    def event_tab_key(self, event):
        """Special tab key event in order to prevent tkinter from cycling through widgets. Has to return break quickly
        or else tkinter will do its own thing."""
        self.window.event_generate("<<event-tab-key-override>>")
        return "break"

    def event_shift_tab_key(self, event):
        """Special shift tab key event in order to prevent tkinter from cycling through widgets. Has to return break
        quickly or else tkinter will do its own thing."""
        self.window.event_generate("<<event-shift-tab-key-override>>")
        return "break"

    def event_tab_key_override(self, event):
        """Special call for tab."""
        distance = len(self.board.current_word.cells) - self.board.current_word.cells.index(self.board.current_cell)
        self.move_current_selection(self.direction, distance, force_next_word=True)

    def event_shift_tab_key_override(self, event):
        """Special call for shift tab."""
        numbering = self.numbering.across if self.direction == ACROSS else self.numbering.down
        last_word_info = numbering[numbering.index(self.board.current_word.info) - 1]
        length = last_word_info["len"]
        distance = self.board.current_word.cells.index(self.board.current_cell) + length
        self.move_current_selection(self.direction, -distance, force_next_word=True)

    def event_key(self, event):
        """Key event for the entire crossword player since canvas widgets have no active state. To add rebus characters
        the shift key is used."""
        modifier = MODIFIERS.get(event.state)
        keysym = event.keysym

        if not self.has_focus(self.chat_entry):
            # Letters
            if keysym.lower() in LETTERS and event.char is not "":
                letters = keysym.upper()
                if modifier == "Shift": letters = self.board.current_cell.letters + letters
                self.write_cell(self.board.current_cell, letters)
                if modifier != "Shift": self.move_current_selection(self.direction, 1)
            elif keysym == "BackSpace":
                if modifier == "Shift": letters = self.board.current_cell.letters[:-1]
                else: letters = ""
                self.write_cell(self.board.current_cell, letters)
                if modifier != "Shift": self.move_current_selection(self.direction, -1)
            elif keysym == "space":
                if config.ON_SPACE_KEY == "change direction":
                    self.direction = [ACROSS, DOWN][[DOWN, ACROSS].index(self.direction)]
                    self.move_current_selection(self.direction, 0)
                else:
                    self.write_cell(self.board.current_cell, " ")
                    self.move_current_selection(self.direction, 1)

            # Movement
            elif keysym == "Return":
                self.window.event_generate("<<event-tab-key-override>>")
            elif keysym == "Left":
                if self.direction != ACROSS:
                    self.direction = ACROSS
                elif config.ON_DOUBLE_ARROW_KEY != "stay in cell":
                    self.move_current_selection(ACROSS, -1, force_next_word=True)
            elif keysym == "Right":
                if self.direction != ACROSS:
                    self.direction = ACROSS
                elif config.ON_DOUBLE_ARROW_KEY != "stay in cell":
                    self.move_current_selection(ACROSS, 1, force_next_word=True)
            elif keysym == "Up":
                if self.direction != DOWN:
                    self.direction = DOWN
                elif config.ON_DOUBLE_ARROW_KEY != "stay in cell":
                    self.move_current_selection(DOWN, -1, force_next_word=True)
            elif keysym == "Down":
                if self.direction != DOWN:
                    self.direction = DOWN
                elif config.ON_DOUBLE_ARROW_KEY != "stay in cell":
                    self.move_current_selection(DOWN, 1, force_next_word=True)

            self.move_current_selection(self.direction, 0)

        self.window.event_generate("<<update-selected-clue>>")

    def event_game_board_button_1(self, event):
        """On button-1 event for the canvas."""
        if self.has_focus(self.chat_entry):
            self.game_board.focus_set()
            return
        x = (event.x - config.CANVAS_OFFSET - 1) // config.CELL_SIZE
        y = (event.y - config.CANVAS_OFFSET - 1) // config.CELL_SIZE
        if not (0 <= x < self.puzzle.width and 0 <= y < self.puzzle.height): return
        self.board.current_word.update_options(fill=config.FILL_DESELECTED)
        if self.board[x, y] == self.board.current_cell: self.direction = ["down", "across"][self.direction == "down"]
        self.board.set_selected(x, y, self.direction)
        self.window.event_generate("<<update-selected-clue>>")
        self.game_board.focus_set()

    def event_game_board_button_2(self, event):
        """On button-2 event for the canvas."""
        if self.has_focus(self.chat_entry):
            self.game_board.focus_set()
            return
        self.game_board.event_generate("<Button-1>")
        self.window.update()
        window_x = self.game_board.winfo_rootx() + event.x
        window_y = self.game_board.winfo_rooty() + event.y
        self.game_menu.post(window_x, window_y)
        self.game_board.focus_set()

    def event_across_list_button_1(self, event):
        """On button-1 and key event for the across clue list."""
        self.board.current_word.update_options(fill=config.FILL_DESELECTED)
        self.direction = "across"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.across[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def event_down_list_button_1(self, event):
        """On button-1 and key event for the down clue list."""
        self.board.current_word.update_options(fill=config.FILL_DESELECTED)
        self.direction = "down"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.down[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def event_chat_entry_return(self, event):
        """On event for when the user presses enter in the chat entry. This is just a filler."""
        self.chat_text.config(state="normal")

        start = self.chat_text.index("end")+"-1l"  # Not sure why
        end = start + "+%ic"%len(self.name)

        self.chat_text.insert("end", "%s: %s" % (self.name, self.chat_entry.get()) + "\n")
        self.chat_text.tag_add("you", start, end)
        self.chat_text.see("end")

        self.chat_text.config(state="disabled")
        self.chat_entry.delete(0, "end")

    def run_application(self):
        """Run the application."""
        logging.log(INFO, "%s application running", repr(self))
        self.epoch = time.time()
        self.window.event_generate("<<update-game-info>>")
        self.window.event_generate("<<update-clock>>")
        self.game_board.focus_set()
        self.window.mainloop()

    def destroy_application(self):
        """Close the application."""
        self.window.quit()
        self.window.destroy()

    def start(self):
        """Convenience function to setup and run the player."""
        self.build_application()
        self.run_application()

    def stop(self):
        """Stop the player."""
        self.destroy_application()
        logging.log(INFO, "%s application destroyed", repr(self))


# Sockets
def send_all(sock, message):
    """Pack the message length and content for sending larger messages."""
    message = struct.pack('>I', len(message)) + message  # Pack the message length and the message
    sock.sendall(message)

def receive_all(sock):
    """Read message length and receive the corresponding amount of data."""
    message_length = _receive_all(sock, 4)  # Unpack the message length
    if not message_length: return None
    message_length = struct.unpack('>I', message_length)[0]  # Unpack the message
    return _receive_all(sock, message_length)

def _receive_all(sock, buffer_size):
    """Secondary function to receive a specified amount of data."""
    message = b''
    while len(message) < buffer_size:
        packet = sock.recv(buffer_size - len(message))
        if not packet: return None
        message += packet
    return message


# Socket Models
class Handler:
    """Server side client handler. Continuously receives data while offering simultaneous sending."""

    def __init__(self, sock, address, server):
        """Magic method to initialize a new handler."""
        self.socket = sock
        self.address = address
        self.server = server

        self.active = False
        logging.log(INFO, "%s initialized", repr(self))

    def __repr__(self):
        """Magic method for string representation."""
        return "[%i] handler (%s)" % (id(self), self.address[0])

    def send(self, message):
        """Send a message to the server using the open socket."""
        data = pickle.dumps(message)
        send_all(self.socket, data)

    def receive(self):
        """Message receive loop. Should be threaded."""
        logging.log(INFO, "%s receive loop started", repr(self))
        while self.active:
            try:
                data = receive_all(self.socket)
                message = pickle.loads(data)
                if message.get("type") == "stop":
                    self.stop()
                self.server.messages.put((self, message))
            except Exception as e:
                logging.log(ERROR, "%s receive loop error: %s", repr(self), e)
                self.stop()
        logging.log(INFO, "%s receive loop stopped", repr(self))

    def start(self):
        """Start a the handler."""
        self.active = True
        self._receive = threading.Thread(target=self.receive)
        self._receive.start()
        logging.log(INFO, "%s started", repr(self))

    def stop(self):
        self.active = False
        logging.log(INFO, "%s socket closed", repr(self))
        self.server.handlers.remove(self)
        logging.log(INFO, "%s stopped", repr(self))

class Server:
    """A simple server for hosting a local network multiplayer crossword game."""

    def __init__(self, address):
        """Magic method to initialize a new server."""
        self.address = address
        self.messages = queue.Queue()
        self.handlers = []
        self.epoch = time.time()
        self.progress = []
        self.active = True

        self.puzzle = puz.read("puzzles/Nov0705.puz")  # For testing                                          # puz.read
        self.puzzle.fill = list(self.puzzle.fill)

        self.numbering = self.puzzle.clue_numbering()
        for clue in self.numbering.across: clue.update({"dir": ACROSS})
        for clue in self.numbering.down: clue.update({"dir": DOWN})
        self.board = Board(self.puzzle, self.numbering)

        logging.log(INFO, "%s initialized", repr(self))

    def __repr__(self):
        """Magic method for string representation."""
        return "server (%s)" % self.address[0]

    def bind(self):
        """Bind the server to the address provided at initialization. If it cannot bind it will quit."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind(self.address)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.listen(5)
            logging.log(INFO, "%s bound" % repr(self))
        except OSError as e:
            logging.log(FATAL, "%s could not bind: %s", repr(self), e)
            quit()

    def send(self, message):
        """Send a message to every handler."""
        for handler in self.handlers:
            handler.send(message)

    def search(self):
        """Loop to search for incoming connections. Should be threaded."""
        logging.log(INFO, "%s search loop started", repr(self))
        while self.active:
            try:
                sock, address = self.socket.accept()
                handler = Handler(sock, address, self)
                self.handlers.append(handler)
                if len(self.handlers) == 1:  # First player
                    self.epoch = time.time()
                handler.start()
                handler.send({"type": "puzzle", "message": self.puzzle})
                handler.send({"type": "epoch", "message": self.epoch})
                handler.send({"type": "progress", "message": self.progress})
            except Exception as e:
                logging.log(ERROR, "%s error in search loop: %s", repr(self), e)
                self.stop()

    def serve(self):
        """Loop to handle all incoming messages. Should run as main."""
        while self.active:
            try:
                if not self.messages.empty():
                    message = self.messages.get()
                    self.handle(message)
            except Exception as e:
                logging.log(ERROR, "%s error in serve loop: %s", repr(self), e)
                self.stop()

    def handle(self, message):
        """Handle messages from the queue."""
        handler, message = message
        if message["type"] == "info":  # Special client message to send information
            handler.color = message["color"]
            handler.name = message["name"]
        else:
            message["color"] = handler.color
            message["name"] = handler.name
            if message["type"] == "game":
                x, y = message["position"]
                self.puzzle.fill[position_to_index(x, y, self.puzzle.width)] = message["letters"]
                self.progress.append(message)
            self.send(message)

    def start(self):
        """Start the server."""
        self.active = True
        self.bind()
        self._search = threading.Thread(target=self.search)
        self._search.start()
        logging.log(INFO, "%s started", repr(self))
        logging.log(INFO, "%s running on %s:%s", repr(self), *self.address)
        try:
            self.serve()
        except KeyboardInterrupt:
            print()
            self.stop()

    def stop(self):
        """Stop the server."""
        if self.active == False:
            return
        self.active = False
        self.socket.close()
        logging.log(INFO, "%s socket closed", repr(self))
        logging.log(INFO, "%s shut down", repr(self))

class Client(Player):
    """A networking framework built on top of the existing crossword player."""

    def __init__(self, address, name, color):
        """Initialize a new, named client connecting to a server address."""
        Player.__init__(self, name, color)

        self.address = address
        self.name = name
        self.color = color
        self.messages = queue.Queue()
        self.active = False
        logging.log(DEBUG, "%s initialized", repr(self))

    def __repr__(self):
        """Magic method for string representation."""
        return "[%i] client (%s)" % (id(self), self.address[0])

    def bind(self):
        try:
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.connect(self.address)
            logging.log(DEBUG, "%s bound", repr(self))
        except OSError as e:
            logging.log(FATAL, "%s could not bind: %s", repr(self), e)
            quit()

    def send(self, message):
        """Send a message to the server."""
        data = pickle.dumps(message)
        send_all(self.socket, data)

    def write_cell(self, cell, letters):
        """Overwrite that allows the client to instead send the letter to the server."""
        position = self.board.index(self.board.current_cell)
        self.send({"type": "game", "position": position, "letters": letters})

    def event_chat_entry_return(self, event):
        """Overwrite that allows the chat entry to send chat messages."""
        message = self.chat_entry.get() + "\n"
        self.chat_entry.delete(0, "end")
        self.send({"type": "chat", "message": message})

    def receive(self):
        """Loop receive data from the connected client. The puzzle clause has to be here because it triggers the start
        of the application, which runs the update loop recursively. Tkinter cannot interact with threads."""
        logging.log(DEBUG, "%s receive loop started", repr(self))
        while self.active:
            try:
                data = receive_all(self.socket)
                message = pickle.loads(data)
                if message["type"] == "puzzle":  # Initial data transaction for setup
                    self.puzzle = message["message"]
                    self.numbering = self.puzzle.clue_numbering()
                    self.board = Board(self.puzzle, self.numbering)
                    self.ready = True  # Let the application build
                else:
                    self.messages.put(message)
            except Exception as e:
                logging.log(ERROR, "%s error in receive loop: %s", repr(self), e)
                if self.active: self.stop()

    def update(self):
        """Update the graphical interface when there are new messages."""
        if not self.active: self.destroy_application()  # Make sure the application is killed if inactive
        while not self.messages.empty():
            message = self.messages.get()
            if message["type"] == "epoch":
                self.epoch = message["message"]
            elif message["type"] == "progress":
                for message in message["message"]:
                    self.messages.put(message)
            elif message["type"] == "stop":
                logging.log(FATAL, "%s received stop", repr(self))
                self.stop()
            elif message["type"] == "game":
                x, y = message["position"]
                self.board[x, y].update_options(color=message["color"], letters=message["letters"])
            elif message["type"] == "chat":
                self.chat_text.config(state="normal")
                start = self.chat_text.index("end")+"-1l"  # Not sure why
                end = start + "+%ic"%len(message["name"])
                self.chat_text.tag_config(message["name"], foreground=message["color"])
                self.chat_text.insert("end", "%s: %s" % (message["name"], message["message"]))
                self.chat_text.tag_add(message["name"], start, end)
                self.chat_text.see("end")
                self.chat_text.config(state="disabled")
        self.window.after(100, self.update)

    def start(self):
        """Start the client."""
        self.ready = False

        self.active = True
        self.bind()
        self.send({"type": "info", "name": self.name, "color": self.color})
        self._receive = threading.Thread(target=self.receive)
        self._receive.start()

        while not self.ready: pass
        self.build_application()
        self.window.after(100, self.update)

        logging.log(DEBUG, "%s update loop started", repr(self))
        logging.log(DEBUG, "%s started", repr(self))

        self.run_application()

    def stop(self):
        """Stop the client."""
        self.active = False
        try: self.destroy_application()
        except: pass  # Application has not been build
        self.send({"type": "stop"})
        self.socket.close()
        logging.log(DEBUG, "%s socket closed", repr(self))
        logging.log(DEBUG, "%s stopped", repr(self))


if len(sys.argv) == 1:
    logging.log(ERROR, "no arguments supplied on execution")
elif sys.argv[1] == "server":
    server = Server((sys.argv[2], int(sys.argv[3])))
    server.start()
elif sys.argv[1] == "client":
    client = Client((sys.argv[2], int(sys.argv[3])), sys.argv[4], sys.argv[5])
    client.start()
elif sys.argv[1] == "test":
    player = Player("Noah", "black")
    player.load_puzzle("puzzles/Nov0705.puz")
    player.start()
else:
    logging.log(ERROR, "invalid argument '%s'", sys.argv[1])


