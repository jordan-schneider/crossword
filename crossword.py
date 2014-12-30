# Crossword
# Noah Kim

# Import
import logging

import tkinter
import time
import datetime
import string

import puz

# Logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
FORMAT = "%(levelname)8s %(asctime)s %(message)s"
DATEFMT = "%I:%M:%S %p" # %m/%d/%y
LEVEL = NOTSET
logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=LEVEL)
logging.log(INFO, "crossword: started")

# Constant
WINDOW_TITLE = "NYTimes Crossword Puzzle"
WINDOW_LINE_FILL = "grey70"
WINDOW_LINE_HEIGHT = 3
WINDOW_SPACE_HEIGHT = 5
WINDOW_CLOCK_COLOR = "grey70"

CANVAS_OFFSET = 3
CANVAS_SPARE = 2 + 1 # 2 for outline and 1 for spare right hand pixels

CELL_SIZE = 40

PAD_LETTER = CELL_SIZE // 2
PAD_NUMBER_LEFT = 3
PAD_NUMBER_TOP = 6

FILL_LETTER_0 = "white"
FILL_LETTER_1 = "light blue"
FILL_LETTER_2 = "yellow"
FILL_EMPTY = "black"

FONT_TITLE = ("tkDefaultFont", 30)
FONT_HEADER = ("tkDefaultFont", 25)
FONT_LABEL = ("tkDefaultFont", 20)
FONT_LIST = ("tkDefaultFont", 15)
FONT_LETTER = ("tkDefaultFont", int(CELL_SIZE / 1.8))
FONT_NUMBER = ("tkDefaultFont", int(CELL_SIZE / 3.5))

TYPE_LETTER = "-"
TYPE_EMPTY = "."

DOWN = "down"
ACROSS = "across"

ON_DOUBLE_ARROW_KEY = ["stay in cell", "move in direction"][0] # TODO
ON_SPACE_KEY = ["clear and skip", "change direction"][0] # TODO
ON_ENTER_KEY = ["next word"][0] # ["rebus mode"]? # TODO
ON_LAST_LETTER_GO_TO = ["next word", "first cell", "same cell"][0]
SHOW_CLOCK = True

logging.log(DEBUG, "crossword: constants initialized")


# Function
def index_to_position(index, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return (index % array_width, index // array_width)


def position_to_index(x, y, array_width):
    """Determine the coordinates of an index in an array of specified width."""
    return x + y*array_width


# Class
class CrosswordCell:
    """Container class for a single crossword cell."""

    def __init__(self, canvas, type, *position, letter="", number=""):
        """Initialize a new crossword cell. Takes tkinter canvas, cell type,
        x and y, and optionally a letter and a number."""
        self.canvas = canvas
        self.type = type
        self.x = position[0]
        self.y = position[1]
        self.letter = letter
        self.number = number

        self.selection_level = 0
        self.canvas_ids = []

    def __repr__(self):
        """Represent the crossword cell as a string. Since there are too many
        created during runtime they are not individually identified."""
        return "CrosswordCell"

    def set_selected(self, level=1):
        """Set whether or not the cell is selected. If the selection level is 1,
        FILL_LETTER_1 will be used. If it is 2, FILL_LETTER_2 will be used.
        Otherwise an error is logged."""
        if level not in (1, 2):
            logging.log(ERROR, "%s: bad selection level '%i'" % (self, level))
            return
        self.selection_level = level
        self.draw_to_canvas()

    def set_unselected(self):
        """Set the cell as unselected (selection level 0). `FILL_LETTER_0` is
        used on draw."""
        self.selection_level = 0
        self.draw_to_canvas()

    def draw_to_canvas(self):
        """Draw the cell, its fill, letter, and number to the canvas at the
        cell's position."""
        self.canvas.delete(*self.canvas_ids)

        x, y = self.x, self.y
        if self.type == TYPE_LETTER:
            cell_position = (x, y, x+CELL_SIZE, y+CELL_SIZE)
            text_position = (x+PAD_LETTER, y+PAD_LETTER)

            if self.selection_level == 0: cell_fill = FILL_LETTER_0
            elif self.selection_level == 1: cell_fill = FILL_LETTER_1
            elif self.selection_level == 2: cell_fill = FILL_LETTER_2
            else: return

            cell_id = self.canvas.create_rectangle(
                *cell_position, fill=cell_fill)
            letter_id = self.canvas.create_text(
                *text_position, text=self.letter, font=FONT_LETTER)
            self.canvas_ids = [cell_id, letter_id]

            if self.number:
                number_position = (x+PAD_NUMBER_LEFT, y+PAD_NUMBER_TOP)
                number_id = self.canvas.create_text(
                    *number_position, text=self.number, font=FONT_NUMBER,
                    anchor="w")
                self.canvas_ids.append(number_id)
        else:
            cell_position = (x, y, x+CELL_SIZE, y+CELL_SIZE)
            cell_fill = FILL_EMPTY
            cell_id = self.canvas.create_rectangle(
                *cell_position, fill=cell_fill)
            self.canvas_ids.append(cell_id)


class CrosswordWord:
    """Container class for a crossword word that contains multiple cells as well
    as its numbering information from the original puzzle."""


    def __init__(self, cells, info):
        """Initialize a new crossword word with its corresponding letter cells
        puzzle info."""
        self.cells = cells
        self.info = info

    def __repr__(self):
        """Represent the crossword cell as a string. Since there are too many
        created during runtime they are not individually identified."""
        return "CrosswordWord"

    def set_selected(self):
        """Set each cell in the word as selected. Does not utilize different
        selection levels."""
        for cell in self.cells:
            cell.set_selected()

    def set_unselected(self):
        """Set the entire word as unselected."""
        for cell in self.cells:
            cell.set_unselected()


class CrosswordBoard:
    """Container class for an entire crossword board. Essentially serves as a
    second layer on top of the puzzle class."""

    def __init__(self, puzzle, numbering):
        """Create a crossword given a puzzle object."""
        self.puzzle = puzzle
        self.numbering = numbering

        self.cells = []
        for y in range(self.puzzle.height):
            self.cells.append([])
            for x in range(self.puzzle.width):
                self.cells[y].append(None)
        self.across_words = []
        self.down_words = []

        self.current_cell = None
        self.current_word = None
        logging.log(DEBUG, "%s: initialized", repr(self))

    def __repr__(self):
        """Represent the crossword cell as a string. Since there is only one
        created during runtime it is not individually identified."""
        return "CrosswordBoard"

    def __setitem__(self, position, value):
        """Implements coordinate based index setting."""
        self.cells[position[1]][position[0]] = value

    def __getitem__(self, position):
        """Implements coordinate based index getting."""
        return self.cells[position[1]][position[0]]

    def index(self, cell):
        """Get the coordinates of a cell if it exists in the crossword board."""
        index = sum(self.cells, []).index(cell)
        return index_to_position(index, self.puzzle.width)

    def generate_words(self):
        """Generates all of the words for the crossword board. Should be part of
        initialization but cannot be because the crossword player has to
        calculate the position and provide the canvas for each cell."""
        for info in self.numbering.across:
            cells = []
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            for i in range(length):
                cells.append(self[x+i, y])
            word = CrosswordWord(cells, info)
            self.across_words.append(word)
        for info in self.numbering.down:
            cells = []
            x, y = index_to_position(info["cell"], self.puzzle.width)
            length = info["len"]
            for i in range(length):
                cells.append(self[x, y+i])
            word = CrosswordWord(cells, info)
            self.down_words.append(word)
        logging.log(DEBUG, "%s: generated words", repr(self))

    def set_selected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the
        direction) as selected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        elif direction == DOWN: words = self.down_words
        else:
            logging.log(ERROR, "%s: invalid direction in set_selected")
            return
        for word in words:
            if origin in word.cells:
                word.set_selected()
                origin.set_selected(level=2)
                self.current_cell = origin
                self.current_word = word

    def set_unselected(self, x, y, direction):
        """Set the word at the position of the origin letter (and of the
        direction) as unselected."""
        origin = self[x, y]
        if direction == ACROSS: words = self.across_words
        elif direction == DOWN: words = self.down_words
        else:
            logging.log(ERROR, "%s: invalid direction in set_unselected")
            return
        for word in words:
            if origin in word.cells:
                word.set_unselected()

class CrosswordPlayer:
    """A single player crossword player that uses puz file crossword puzzles."""

    def __init__(self):
        """Initialize a new crossword player."""
        self.direction = "across"

    def __repr__(self):
        """Represent the crossword cell as a string. Since there is only one
        created during runtime it is not individually identified."""
        return "CrosswordPlayer"

    def load_puzzle(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)
        self.numbering = self.puzzle.clue_numbering()
        for clue in self.numbering.across:
            clue.update({"dir": ACROSS})
        for clue in self.numbering.down:
            clue.update({"dir": DOWN})
        self.board = CrosswordBoard(self.puzzle, self.numbering)

    def build_application(self):
        """Build the graphical interface of the crossword player. Also draws the
        crossword board and populates the clue lists."""
        self.window = tkinter.Tk()
        self.window.title(WINDOW_TITLE)
        self.window.resizable(False, False)
        self.window.bind_all("<Key>", self.on_key_event)

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill="both", padx=5, pady=5)

        self.title = tkinter.Label(self.frame)
        self.title.config(text=self.puzzle.title[10:], font=FONT_TITLE)
        self.title.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.author = tkinter.Label(self.frame)
        self.author.config(text=self.puzzle.author, font=FONT_TITLE)
        self.author.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.line = tkinter.Frame(self.frame)
        self.line.config(height=WINDOW_LINE_HEIGHT, bg=WINDOW_LINE_FILL)
        self.line.grid(row=1, column=0, columnspan=2, padx=5, sticky="we")

        self.space = tkinter.Frame(self.frame)
        self.space.config(height=WINDOW_SPACE_HEIGHT)
        self.space.grid(row=2, column=0, columnspan=2, padx=8, sticky="we")

        self.game = tkinter.Frame(self.frame)
        self.game.grid(row=3, column=0)

        self.game_info = tkinter.Label(self.game)
        self.game_info.config(font=FONT_HEADER, anchor="w")
        self.game_info.grid(row=0, column=0, padx=5, pady=5, sticky="we")

        self.game_clock = tkinter.Label(self.game)
        self.game_clock.config(font=FONT_HEADER, fg=WINDOW_CLOCK_COLOR)
        self.game_clock.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        if not SHOW_CLOCK:
            self.game_clock.config("white")

        self.game_board = tkinter.Canvas(self.game)
        self.game_board.config(
            width=CELL_SIZE*self.puzzle.width + CANVAS_SPARE,
            height=CELL_SIZE*self.puzzle.height + CANVAS_SPARE)
        self.game_board.grid(
            row=1, column=0, padx=5-CANVAS_OFFSET, pady=5-CANVAS_OFFSET,
            sticky="nwe")
        self.game_board.bind("<Button-1>", self.on_board_button1)
        self.game_board.bind("<Button-2>", self.on_board_button2)

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
        self.across_label.config(text="Across", anchor="w", font=FONT_LABEL)
        self.across_label.grid(row=0, column=0, sticky="w")

        self.across_list = tkinter.Listbox(self.across)
        self.across_list.config(
            width=35, font=FONT_LIST, bd=0, selectborderwidth=0,
            selectbackground="light blue")
        self.across_list.grid(row=1, column=0, sticky="ns")
        self.across_list.bind("<Button-1>", self.on_across_list_button1)

        self.down = tkinter.Frame(self.clues)
        self.down.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        self.down.rowconfigure(1, weight=1)

        self.down_label = tkinter.Label(self.down)
        self.down_label.config(text="Down", anchor="w", font=FONT_LABEL)
        self.down_label.grid(row=0, column=0, sticky="w")

        self.down_list = tkinter.Listbox(self.down)
        self.down_list.config(
            width=35, font=FONT_LIST, bd=0, selectborderwidth=0,
            selectbackground="light blue")
        self.down_list.grid(row=1, column=0, sticky="ns")
        self.down_list.bind("<Button-1>", self.on_down_list_button1)

        logging.log(DEBUG, "%s: built graphical interface", repr(self))

        self.game_board.create_rectangle(
            CANVAS_OFFSET, CANVAS_OFFSET,
            CELL_SIZE*self.puzzle.width + CANVAS_OFFSET,
            CELL_SIZE*self.puzzle.height + CANVAS_OFFSET)

        numbers = {w["cell"]: w["num"] for w in self.numbering.across}
        numbers.update({w["cell"]: w["num"] for w in self.numbering.down})
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = CrosswordCell(
                    self.game_board,
                    self.puzzle.fill[y*self.puzzle.height + x],
                    CANVAS_OFFSET + x*CELL_SIZE,
                    CANVAS_OFFSET + y*CELL_SIZE,
                    number=numbers.get(y*self.puzzle.height + x, "")
                )
                self.board[x, y] = cell
                cell.draw_to_canvas()
        self.board.generate_words()

        logging.log(DEBUG, "%s: created crossword cells", repr(self))
        logging.log(DEBUG, "%s: drew crossword puzzle", repr(self))

        for info in self.numbering.across:
            self.across_list.insert("end", " %(num)i. %(clue)s" % info)
        for info in self.numbering.down:
            self.down_list.insert("end", " %(num)i. %(clue)s" % info)
        self.across_list.selection_set(0)

        logging.log(DEBUG, "%s: populated clue lists", repr(self))

        self.board.set_selected(0, 0, self.direction)

    def get_selected_clue(self):
        """Get which clue in the clue lists is selected."""
        selection = self.across_list.curselection()
        if selection:
            return self.numbering.across[int(selection[0])]
        selection = self.down_list.curselection()
        if selection:
            return self.numbering.down[int(selection[0])]

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
            self.across_list.selection_set(
                self.numbering.across.index(word.info))
            self.across_list.see(self.numbering.across.index(word.info))
        else:
           self.down_list.selection_clear(0, "end")
           self.down_list.selection_set(
                self.numbering.down.index(word.info))
           self.down_list.see(self.numbering.down.index(word.info))

    def update_clock(self, event=None):
        """Update the game time."""
        seconds = time.time() - self.epoch
        clock_time = str(datetime.timedelta(seconds=int(seconds)))
        self.game_clock.config(text=clock_time)
        self.window.after(100, self.update_clock)

    def move_current_selection(self, direction, distance):
        """Move the current selection by the distance in the specified
        direction. Skips to next word and wraps around the entire board."""
        x, y = self.board.index(self.board.current_cell)
        s = -1 if distance < 0 else 1
        if direction == ACROSS:
            for i in range(0, distance, s):
                at_word_end = False
                if x + s >= self.puzzle.width:
                    at_word_end = True
                else:
                    if not self.board[x+s, y] in self.board.current_word.cells:
                        at_word_end = True

                if at_word_end:
                    cell_info_index = self.numbering.across.index(
                        self.board.current_word.info)
                    next_cell_info = self.numbering.across[
                        (cell_info_index + s) % len(self.numbering.across)]
                    next_cell_number = next_cell_info["cell"]
                    x, y = index_to_position(
                        next_cell_number, self.puzzle.width)

                    if s < 0:
                        x += s
                else:
                    x += s
            self.board.set_selected(x, y, self.direction)
        if direction == DOWN:
            for i in range(distance):
                at_word_end = False
                if y + s >= self.puzzle.height:
                    at_word_end = True
                else:
                    if not self.board[x, y+s] in self.board.current_word.cells:
                        at_word_end = True

                if at_word_end:
                    cell_info_index = self.numbering.down.index(
                        self.board.current_word.info)
                    next_cell_info = self.numbering.down[
                        (cell_info_index + s) % len(self.numbering.down)]
                    next_cell_number = next_cell_info["cell"]
                    x, y = index_to_position(
                        next_cell_number, self.puzzle.width)
                    
                else:
                    y += s
            self.board.set_selected(x, y, self.direction)
        
    def on_board_button1(self, event):
        """On button-1 event for the canvas."""
        x = (event.x - CANVAS_OFFSET - 1) // CELL_SIZE
        y = (event.y - CANVAS_OFFSET - 1) // CELL_SIZE
        if not (0 <= x < self.puzzle.width and 0 <= y < self.puzzle.height):
            return

        self.board.current_word.set_unselected()
        if self.board[x, y] == self.board.current_cell:
            self.direction = "across" if self.direction == "down" else "down"
        self.board.set_selected(x, y, self.direction)

        self.update_selected_clue()

    def on_board_button2(self, event):
        """On button-2 event for the canvas."""
        window_x = self.game_board.winfo_rootx() + event.x
        window_y = self.game_board.winfo_rooty() + event.y
        self.game_menu.post(window_x, window_y)

    def on_across_list_button1(self, event):
        """On button-1 event for the across clue list."""
        self.board.current_word.set_unselected()
        self.direction = "across"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.across[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def on_down_list_button1(self, event):
        """On button-1 event for the down clue list."""
        self.board.current_word.set_unselected()
        self.direction = "down"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.down[clue_number]["cell"]
        x, y = index_to_position(cell_number, self.puzzle.width)
        self.board.set_selected(x, y, self.direction)

    def on_key_event(self, event):
        """On key event for the entire crossword player since canvas widgets
        have no active state."""
        if event.char in string.ascii_letters + " ":
            letter = event.char if event.char != " " else ""
            self.board.current_cell.letter = letter.capitalize()
            self.board.current_cell.draw_to_canvas()

            x, y = self.board.index(self.board.current_cell) 
    
            at_word_end = False
            if x + 1 >= self.puzzle.width:
                at_word_end = True
            else:
                if not self.board[x+1, y] in self.board.current_word.cells:
                    at_word_end = True

            if at_word_end:
                if ON_LAST_LETTER_GO_TO == "first cell":
                    distance = self.board.current_word.info["len"] - 1
                    self.move_current_selection(self.direction, -distance)
                elif ON_LAST_LETTER_GO_TO == "same cell":
                    pass                    
                else:
                    self.move_current_selection(self.direction, 1)
            else:
                self.move_current_selection(self.direction, 1)

            self.update_selected_clue()

        elif event.keysym == "BackSpace":
            self.board.current_cell.letter = ""
            self.board.current_cell.draw_to_canvas()

            self.move_current_selection(self.direction, -1)
                
    def run_application(self):
        """Run the application."""
        logging.log(INFO, "%s: running application", repr(self))
        self.epoch = time.time()
        self.update_game_info()
        self.update_clock()
        self.window.mainloop()

    def destroy_application(self):
        """Close the application."""
        self.window.quit()
        self.window.destroy()
        logging.log(INFO, "%s: destroying application", repr(self))

cp = CrosswordPlayer()
cp.load_puzzle("puzzles/Nov0705.puz")
cp.build_application()
cp.run_application()
