# Graphics
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
FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATEFMT = "%m/%d/%y %I:%M:%S %p"
LEVEL = NOTSET
logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=LEVEL)

# Constant
WINDOW_TITLE = "New York Times Crossword Puzzle"

CANVAS_PAD = 3

CELL_SIDE = 40
CELL_TEXT_PAD = CELL_SIDE//2
CELL_NUMBER_PAD = 3
CELL_NUMBER_PAD2 = 6
CELL_LETTER_FILL = "white"
CELL_LETTER_FILL2 = "light blue"
CELL_LETTER_FILL3 = "yellow"
CELL_EMPTY_FILL = "black"

TITLE_FONT = ("tkDefaultFont", 30)
HEADER_FONT = ("tkDefaultFont", 25)
LABEL_FONT = ("tkDefaultFont", 20)
LIST_FONT = ("tkDefaultFont", 15)
LETTER_FONT = ("tkDefaultFont", int(CELL_SIDE/1.8))
NUMBER_FONT = ("tkDefaultFont", int(CELL_SIDE/3.5))

LETTER_CELL = "-"
BLACK_CELL = "."

# Crossword
class CrosswordCell:
    """A single crossword puzzle cell."""

    def __init__(self, board, type, *position, letter="", number=""):
        """Initialize a new crossword cell."""
        self.board = board
        self.type = type
        self.x, self.y = position
        self.letter = letter
        self.number = number

        self.drawings = []
        self.selected = 0

    def set_selected(self, level=1):
        """Select this cell."""
        self.selected = level
        self.draw()

    def set_unselected(self):
        """Deselect this cell."""
        self.selected = 0
        self.draw()

    def draw(self):
        """Draw the cell to the board."""
        self.board.delete(*self.drawings)
        if self.type == LETTER_CELL:
            position = (self.x, self.y, self.x+CELL_SIDE, self.y+CELL_SIDE)
            text_position = (self.x+CELL_TEXT_PAD, self.y+CELL_TEXT_PAD)
            number_position = (self.x+CELL_NUMBER_PAD, self.y+CELL_NUMBER_PAD2)

            fill = CELL_LETTER_FILL2 if self.selected else CELL_LETTER_FILL
            if self.selected == 2:
                fill = CELL_LETTER_FILL3

            cell = self.board.create_rectangle(*position, fill=fill)
            letter = self.board.create_text(
                *text_position, text=self.letter, font=LETTER_FONT)
            
            self.drawings = [cell, letter]
            if self.number:
                number = self.board.create_text(
                    *number_position, text=self.number, font=NUMBER_FONT,
                    anchor="w")
                self.drawings.append(number)

        else:
            position = (self.x, self.y, self.x+CELL_SIDE, self.y+CELL_SIDE)
            fill = CELL_EMPTY_FILL
            
            cell = self.board.create_rectangle(*position, fill=fill)
            self.drawings = [cell]

class CrosswordWord:
    """A series of crossword cells that are part of a word."""

    def __init__(self, cells, direction, clue_number):
        """Initialize a new crossword word."""
        self.cells = cells
        self.direction = direction
        self.clue_number = clue_number

    def set_selected(self):
        """Select the entire word."""
        for cell in self.cells:
            cell.set_selected()

    def set_unselected(self):
        """Unselect the entire word."""
        for cell in self.cells:
            cell.set_unselected()

class CrosswordBoard:
    """A crossword board that keeps track of words and cells."""

    def __init__(self, puzzle):
        """Initialize a new crossword board."""
        self.puzzle = puzzle
        self.numbering = puzzle.clue_numbering()
        self.cells = []
        for y in range(self.puzzle.height):
            self.cells.append([])
            for x in range(self.puzzle.width):
                self.cells[y].append(None)

        self.word = None

    def __setitem__(self, position, value):
        """CrosswordBoard[x, y] = value"""
        self.cells[position[1]][position[0]] = value

    def __getitem__(self, position):
        """CrosswordBoard[x, y]"""
        return self.cells[position[1]][position[0]]

    def process_words(self):
        """Process the words for the puzzle."""
        self.across_words = []
        for clue in self.numbering.across:
            cells = []
            x = clue["cell"] % self.puzzle.width
            y = clue["cell"] // self.puzzle.width
            for i in range(clue["len"]):
                cells.append(self[x+i, y])
            word = CrosswordWord(cells, "A", self.numbering.across.index(clue))
            self.across_words.append(word)
        self.down_words = []
        for clue in self.numbering.down:
            cells = []
            x = clue["cell"] % self.puzzle.width
            y = clue["cell"] // self.puzzle.width
            for i in range(clue["len"]):
                cells.append(self[x, y+i])
            word = CrosswordWord(cells, "D", self.numbering.down.index(clue))
            self.down_words.append(word)

    def set_selected(self, x, y, direction):
        """Set the word and letter at the position to selected."""
        original = self[x, y]
        if direction == "across":
            words = self.across_words
        else:
            words = self.down_words
        for word in words:
            if original in word.cells:
                word.set_selected()
                self.word = word
            original.set_selected(level=2)

    def set_unselected(self, x, y, direction):
        """Set the word and letter at the position to unselected."""
        original = self[x, y]
        if direction == "across":
            words = self.across_words
        else:
            words = self.down_words
        for word in words:
            if original in word.cells:
                word.set_unselected()
            
class CrosswordApplication:
    """A crossword game window."""

    def build_application(self):
        """Build the graphical interface."""
        self.window = tkinter.Tk()
        self.window.title(WINDOW_TITLE)
        self.window.resizable(False, False)
        self.window.bind_all("<Key>", self.on_key)

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill="both", padx=5, pady=5)

        self.title = tkinter.Label(self.frame)
        self.title.config(text=self.puzzle.title[10:], font=TITLE_FONT)
        self.title.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        self.author = tkinter.Label(self.frame)
        self.author.config(text=self.puzzle.author, font=TITLE_FONT)
        self.author.grid(
            row=0, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        self.line = tkinter.Frame(self.frame)
        self.line.config(height=3, bg="grey70")
        self.line.grid(row=1, column=0, columnspan=2, padx=5, sticky="we")

        self.space = tkinter.Frame(self.frame)
        self.space.config(height=5)
        self.space.grid(row=2, column=0, columnspan=2, padx=8, sticky="we")

        self.game = tkinter.Frame(self.frame)
        self.game.grid(row=3, column=0)

        self.game_info = tkinter.Label(self.game)
        self.game_info.config(font=HEADER_FONT, anchor="w")
        self.game_info.grid(row=0, column=0, padx=5, pady=1, sticky="we")

        self.game_clock = tkinter.Label(self.game)
        self.game_clock.config(text="00:00:00", font=TITLE_FONT, fg="grey70")
        self.game_clock.grid(row=0, column=0, padx=5, pady=1, sticky="e")

        self.game_board = tkinter.Canvas(self.game)
        self.game_board.config(
            width=CELL_SIDE*self.puzzle.width + 3,
            height=CELL_SIDE*self.puzzle.height + 3)
        self.game_board.grid(
            row=1, column=0, padx=5-CANVAS_PAD, pady=5-CANVAS_PAD, sticky="nwe")
        self.game_board.bind("<Button-1>", self.on_board_button1)

        self.clues = tkinter.Frame(self.frame)
        self.clues.grid(row=3, column=1, rowspan=2, sticky="ns")
        self.clues.rowconfigure(0, weight=1)
        self.clues.rowconfigure(1, weight=1)

        self.across = tkinter.Frame(self.clues)
        self.across.grid(row=0, column=0, padx=5, pady=5, sticky="ns")
        self.across.rowconfigure(1, weight=1)

        self.across_label = tkinter.Label(self.across)
        self.across_label.config(text="Across", anchor="w", font=LABEL_FONT)
        self.across_label.grid(row=0, column=0, sticky="w")

        self.across_list = tkinter.Listbox(self.across)
        self.across_list.config(
            width=35, font=LIST_FONT, bd=0, selectborderwidth=0,
            selectbackground="light blue")
        self.across_list.grid(row=1, column=0, sticky="ns")
        self.across_list.bind("<Button-1>", self.on_across_list_button1)

        self.down = tkinter.Frame(self.clues)
        self.down.grid(row=1, column=0, padx=5, pady=5, sticky="ns")
        self.down.rowconfigure(1, weight=1)

        self.down_label = tkinter.Label(self.down)
        self.down_label.config(text="Down", anchor="w", font=LABEL_FONT)
        self.down_label.grid(row=0, column=0, sticky="w")

        self.down_list = tkinter.Listbox(self.down)
        self.down_list.config(
            width=35, font=LIST_FONT, bd=0, selectborderwidth=0,
            selectbackground="light blue")
        self.down_list.grid(row=1, column=0, sticky="ns")
        self.down_list.bind("<Button-1>", self.on_down_list_button1)

        self.game_board.create_rectangle(
            CANVAS_PAD, CANVAS_PAD, CELL_SIDE*self.puzzle.width + CANVAS_PAD,
            CELL_SIDE*self.puzzle.height + CANVAS_PAD)

        numbers = {w["cell"]: w["num"] for w in self.numbering.across}
        numbers.update({w["cell"]: w["num"] for w in self.numbering.down})
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = CrosswordCell(
                    self.game_board,
                    self.puzzle.fill[y*self.puzzle.height + x],
                    CANVAS_PAD + x*CELL_SIDE,
                    CANVAS_PAD + y*CELL_SIDE,
                    number=numbers.get(y*self.puzzle.height + x, "")
                )
                self.board[x, y] = cell
                cell.draw()
        self.board.process_words()

        for clue in self.numbering.across:
            self.across_list.insert("end", " %(num)i. %(clue)s" % clue)
        for clue in self.numbering.down:
            self.down_list.insert("end", " %(num)i. %(clue)s" % clue)
        self.across_list.selection_set(0)

        self.last_clicked = (0, 0)
        self.direction = "across"
        self.board.set_selected(0, 0, self.direction)

    def get_selected_clue(self):
        """Get the selected clue."""
        selection = self.across_list.curselection()
        if selection:
            return self.numbering.across[int(selection[0])]
        selection = self.down_list.curselection()
        if selection:
            return self.numbering.down[int(selection[0])]

    def update_game_info(self, event=None):
        """Update the current game info."""
        clue = self.get_selected_clue()
        self.game_info.config(text="%(num)i%(dir)s. %(clue)s" % clue)
        self.window.after(100, self.update_game_info)

    def update_selected_clue(self):
        """Update the selected clue."""
        word = self.board.word
        if word.direction == "A":
            self.across_list.selection_clear(0, "end")
            self.across_list.selection_set(word.clue_number)
            self.across_list.see(word.clue_number)
        else:
           self.down_list.selection_clear(0, "end")
           self.down_list.selection_set(word.clue_number)
           self.down_list.see(word.clue_number)

    def update_clock(self, event=None):
        """Update the game time."""
        seconds = time.time() - self.epoch
        self.game_clock.config(text=str(datetime.timedelta(seconds=int(seconds))))
        self.window.after(100, self.update_clock)

    def load_puzzle(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)
        self.numbering = self.puzzle.clue_numbering()
        for clue in self.numbering.across:
            clue.update({"dir": "A"})
        for clue in self.numbering.down:
            clue.update({"dir": "D"})
        self.board = CrosswordBoard(self.puzzle)        

    def on_board_button1(self, event):
        """Event function for board click."""
        x = (event.x - CANVAS_PAD - 1) // (CELL_SIDE)
        y = (event.y - CANVAS_PAD - 1) // (CELL_SIDE)
        if not (0 <= x < self.puzzle.width and 0 <= y < self.puzzle.height):
            return
        
        self.board.set_unselected(self.last_clicked[0], self.last_clicked[1],
                                  self.direction)
        if (x, y) == self.last_clicked:
            self.direction = "across" if self.direction == "down" else "down"
        self.board.set_selected(x, y, self.direction)
        self.last_clicked = (x, y)

        self.update_selected_clue()

    def on_across_list_button1(self, event):
        """Event function for click on across list."""
        self.board.set_unselected(self.last_clicked[0], self.last_clicked[1],
                                  self.direction)

        self.direction = "across"
        clue_number = self.across_list.nearest(event.y)
        cell_number = self.numbering.across[clue_number]["cell"]
        x = cell_number % self.puzzle.width
        y = cell_number // self.puzzle.width
        
        self.board.set_selected(x, y, self.direction)
        self.last_clicked = (x, y)

    def on_down_list_button1(self, event):
        """Event function for click on across list."""
        self.board.set_unselected(self.last_clicked[0], self.last_clicked[1],
                                  self.direction)

        self.direction = "down"
        clue_number = self.down_list.nearest(event.y)
        cell_number = self.numbering.down[clue_number]["cell"]
        x = cell_number % self.puzzle.width
        y = cell_number // self.puzzle.width
        
        self.board.set_selected(x, y, self.direction)
        self.last_clicked = (x, y)

    def on_key(self, event):
        """Event function for typed letter."""
        letter = event.char
        if letter not in string.ascii_letters:
            return
        x, y = self.last_clicked
        self.board[x, y].letter = letter.capitalize()
        self.board[x, y].draw()
        if self.direction == "across":
            self.board.set_unselected(
                self.last_clicked[0], self.last_clicked[1], self.direction)
            if self.board[x+1, y] not in self.board.word.cells:
                cell_clue = self.numbering.across[self.board.word.clue_number+1]
                cell_number = cell_clue["cell"]
                x = cell_number % self.puzzle.width - 1 # Cheap workaround
                y = cell_number // self.puzzle.width 
            self.board.set_selected(x+1, y, self.direction)
            self.last_clicked = (x+1, y)
            
        else:
            self.board.set_unselected(
                self.last_clicked[0], self.last_clicked[1], self.direction)
            if self.board[x, y+1] not in self.board.word.cells:
                cell_clue = self.numbering.down[self.board.word.clue_number+1]
                cell_number = cell_clue["cell"]
                x = cell_number % self.puzzle.width
                y = cell_number // self.puzzle.width - 1 # Cheap workaround
            self.board.set_selected(x, y+1, self.direction)
            self.last_clicked = (x, y+1)
            
    def run_application(self):
        """Run the application."""
        self.epoch = time.time()
        self.update_game_info()
        self.update_clock()
        self.window.mainloop()

    def destroy_application(self):
        """Close the application."""
        self.window.quit()
        self.window.destroy()
        

ca = CrosswordApplication()
ca.load_puzzle("puzzles/Nov0705.puz")
ca.build_application()
ca.run_application()
