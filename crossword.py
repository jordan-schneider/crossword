# Crossword
# Noah Kim


# Import
import logging
import tkinter
import time
import datetime
import platform
import string
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
    FILL_UNSELECTED = "white"
    FILL_SELECTED_WORD = "light blue"
    FILL_SELECTED_LETTER = "yellow"
    FILL_EMPTY = "black"
    FILL_CORRECT = "green"
    FILL_INCORRECT = "red"
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
    CANVAS_SPARE = 2 + 1  # 2 for outline and 1 for spare right hand pixels

    @property
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

    FILE_CONFIG = "config.txt" # Very meta (._.)
    
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

class CrosswordCell:
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

class CrosswordWord:
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

class CrosswordBoard:
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

        for y in range(self.puzzle.height):
            self.cells.append([])
            for x in range(self.puzzle.width):
                self.cells[y].append(None)

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
            self.across_words.append(CrosswordWord(cells, info, solution))
        for info in self.numbering.down:
            cells = []
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            cells = [self[x, y+i] for i in range(length)]
            solution = "".join([self.puzzle.solution[info["cell"] + i] for i in range(length)])
            self.down_words.append(CrosswordWord(cells, info, solution))
        logging.log(DEBUG, "crossword words generated")

    def set_selected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the direction) as selected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        elif direction == DOWN: words = self.down_words
        if self.current_word:
            self.current_word.update_options(fill=config.FILL_UNSELECTED)
        for word in words:
            if origin in word.cells:
                word.update_options(fill=config.FILL_SELECTED_WORD)
                origin.update_options(fill=config.FILL_SELECTED_LETTER)
                self.current_cell = origin
                self.current_word = word

    def set_unselected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the direction) as unselected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        elif direction == DOWN: words = self.down_words
        for word in words:
            if origin in word.cells:
                word.update_options(fill=config.FILL_UNSELECTED)


# Application Classes
class CrosswordPlayer:
    """The bare client crossword player. Handles nothing except for the crossword board."""

    def __init__(self):
        """Magic method to initialize a new crossword player."""
        self.direction = "across"

    def load_puzzle(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)
        self.numbering = self.puzzle.clue_numbering()
        for clue in self.numbering.across: clue.update({"dir": ACROSS})
        for clue in self.numbering.down: clue.update({"dir": DOWN})
        self.board = CrosswordBoard(self.puzzle, self.numbering)

    def build_application(self):
        """Build the graphical interface, draws the crossword board, and populates the clue lists."""
        self.window = tkinter.Tk()
        self.window.title(config.WINDOW_TITLE)
        self.window.resizable(False, False)
        self.window.bind_all("<Key>", self.on_key_event)

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
            height=config.CELL_SIZE*self.puzzle.height + config.CANVAS_SPARE)
        self.game_board.grid(row=1, column=0, padx=5-config.CANVAS_OFFSET, pady=5-config.CANVAS_OFFSET, sticky="nwe")
        self.game_board.bind("<Button-1>", self.on_board_button1)
        self.game_board.bind("<Button-2>" if platform.system() == "Darwin" else "<Button-3>", self.on_board_button2)

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
        self.across_list.bind("<Button-1>", self.on_across_list_action)

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
        self.down_list.bind("<Button-1>", self.on_down_list_action)
        logging.log(DEBUG, "built crossword graphical interface")

        self.game_board.create_rectangle(
            config.CANVAS_OFFSET, config.CANVAS_OFFSET,
            config.CELL_SIZE*self.puzzle.width + config.CANVAS_OFFSET,
            config.CELL_SIZE*self.puzzle.height + config.CANVAS_OFFSET)

        numbers = {w["cell"]: w["num"] for w in self.numbering.across}
        numbers.update({w["cell"]: w["num"] for w in self.numbering.down})
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = CrosswordCell(
                    self.game_board, self.puzzle.fill[y*self.puzzle.height + x], config.FONT_COLOR,
                    config.FILL_UNSELECTED, config.CANVAS_OFFSET + x*config.CELL_SIZE,
                    config.CANVAS_OFFSET + y*config.CELL_SIZE, number=numbers.get(y*self.puzzle.height + x, ""))
                self.board[x, y] = cell
                cell.draw_to_canvas()
        self.board.generate_words()
        logging.log(DEBUG, "created crossword cells")
        logging.log(DEBUG, "drew crossword puzzle")

        for info in self.numbering.across: self.across_list.insert("end", " %(num)i. %(clue)s" % info)
        for info in self.numbering.down: self.down_list.insert("end", " %(num)i. %(clue)s" % info)
        self.across_list.selection_set(0)
        logging.log(DEBUG, "populated clue lists")

        self.board.set_selected(0, 0, self.direction)

    def get_selected_clue(self):
        """Get which clue in the clue lists is selected."""
        selection = self.across_list.curselection()
        if selection: return self.numbering.across[int(selection[0])]
        selection = self.down_list.curselection()
        if selection: return self.numbering.down[int(selection[0])]

    def update_game_info(self, event=None):
        """Update the current game info."""
        clue = self.get_selected_clue().copy()
        clue["dir"] = clue["dir"][0].capitalize()
        self.game_info.config(text="%(num)i%(dir)s. %(clue)s" % clue)
        self.window.after(100, self.update_game_info)

    def update_selected_clue(self):
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

    def update_clock(self, event=None):
        """Update the game time."""
        seconds = time.time() - self.epoch
        clock_time = str(datetime.timedelta(seconds=int(seconds)))
        self.game_clock.config(text=clock_time)
        self.window.after(100, self.update_clock)

    def move_current_selection(self, direction, distance, force_next_word=False):
        """Move the current selection by the distance in the specified direction."""
        x, y = self.board.index(self.board.current_cell)
        s = -1 if distance < 0 else 1
        self.board.set_selected(x, y, direction)
        self.direction = direction
        if direction == ACROSS:
            for i in range(0, distance, s):
                if x + s >= self.puzzle.width: at_word_end = True
                elif not self.board[x+s, y] in self.board.current_word.cells: at_word_end = True
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
                        self.board.current_word.update_options(fill=config.FILL_UNSELECTED)
                        if s == -1: x += next_cell_info["len"] - 1
                else:
                    x += s
            self.board.set_selected(x, y, self.direction)
        elif direction == DOWN:
            for i in range(0, distance, s):
                if y + s >= self.puzzle.height: at_word_end = True
                elif not self.board[x, y+s] in self.board.current_word.cells: at_word_end = True
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
                        self.board.current_word.update_options(fill=config.FILL_UNSELECTED)
                        if s == -1: y += next_cell_info["len"] - 1
                else:
                    y += s
            self.board.set_selected(x, y, self.direction)

    def on_board_button1(self, event):
        """On button-1 event for the canvas."""
        x = (event.x - config.CANVAS_OFFSET - 1) // config.CELL_SIZE
        y = (event.y - config.CANVAS_OFFSET - 1) // config.CELL_SIZE
        if not (0 <= x < self.puzzle.width and 0 <= y < self.puzzle.height): return
        self.board.current_word.update_options(fill=config.FILL_UNSELECTED)
        if self.board[x, y] == self.board.current_cell: self.direction = ["down", "across"][self.direction == "down"]
        self.board.set_selected(x, y, self.direction)
        self.update_selected_clue()

    def on_board_button2(self, event):
        """On button-2 event for the canvas."""
        self.on_board_button1(event)
        self.window.update()
        window_x = self.game_board.winfo_rootx() + event.x
        window_y = self.game_board.winfo_rooty() + event.y
        self.game_menu.post(window_x, window_y)

    def on_across_list_action(self, event):
        """On button-1 and key event for the across clue list."""
        self.board.current_word.update_options(fill=config.FILL_UNSELECTED)
        self.direction = "across"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.across[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def on_down_list_action(self, event):
        """On button-1 and key event for the down clue list."""
        self.board.current_word.update_options(fill=config.FILL_UNSELECTED)
        self.direction = "down"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.down[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def on_key_event(self, event):
        """On key event for the entire crossword player since canvas widgets
        have no active state."""
        if event.char in string.ascii_letters + " " and event.char is not "":
            letter = event.char if event.char != " " else ""
            self.board.current_cell.update_options(letters=letter.capitalize())
            self.move_current_selection(self.direction, 1)
            self.update_selected_clue()
        elif event.keysym == "BackSpace":
            self.board.current_cell.update_options(letters="")
            self.move_current_selection(self.direction, -1)
        elif event.char == "+": # Rebus
            current_letters = self.board.current_cell.letters
            if len(current_letters) > 0:
                self.board.current_cell.update_options(letters=current_letters+"_")
        elif event.char == "-": # Rebus
            current_letters = self.board.current_cell.letters
            if len(current_letters) > 1:
                self.board.current_cell.update_options(letters=current_letters[:-1])

        elif event.keysym == "Left":
            self.move_current_selection(ACROSS, -1, force_next_word=True)
        elif event.keysym == "Right":
            self.move_current_selection(ACROSS, 1, force_next_word=True)
        elif event.keysym == "Up":
            self.move_current_selection(DOWN, -1, force_next_word=True)
        elif event.keysym == "Down":
            self.move_current_selection(DOWN, 1, force_next_word=True)

    def run_application(self):
        """Run the application."""
        logging.log(INFO, "application running")
        self.epoch = time.time()
        self.update_game_info()
        self.update_clock()
        self.window.mainloop()

    def destroy_application(self):
        """Close the application."""
        self.window.quit()
        self.window.destroy()
        logging.log(INFO, "destroying application")

def test():
    cp = CrosswordPlayer()
    cp.load_puzzle("puzzles/Nov0705.puz")
    cp.build_application()
    cp.run_application()

test()