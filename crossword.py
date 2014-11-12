# Crossword
# Noah Kim, Jordan Schneider

# Logging
import logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATEFMT = "%m/%d/%y %I:%M:%S %p"
LEVEL = NOTSET
logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=LEVEL)

# Import
import tkinter
import string

# Local
import puz

# Constant
CANVAS_MARGIN_INNER = 6
CANVAS_MARGIN_OUTER = 6

CELL_WIDTH = 35
CELL_HEIGHT = 35


LETTER_CELL = "-"
BLACK_CELL = "."

# Graphical
class Cell:
    """Single crossword puzzle cell."""

    def __init__(self, canvas, type, x1, y1, x2, y2, letter="", number=""):
        """Initialize a new crossword cell."""
        self.canvas = canvas
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.type = type
        self.letter = letter
        self.number = number

        self.square_id = 0
        self.letter_id = 0
        self.number_id = 0
        self.fill_id = 0

        self.selected = False

    def draw(self):
        """Draw cell onto the canvas."""
        self.canvas.delete(self.square_id, self.letter_id, self.number_id,
                           self.fill_id)
                    
        if self.type == LETTER_CELL:
            if self.selected:
                self.fill_id = self.canvas.create_rectangle(
                    self.x1, self.y1, self.x2, self.y2, fill="grey85")
                    
            self.square_id = self.canvas.create_rectangle(
                self.x1, self.y1, self.x2, self.y2)
            self.letter_id = self.canvas.create_text(
                (self.x1+self.x2)/2, (self.y1+self.y2)/2, text=self.letter,
                font=("Arial", int(CELL_HEIGHT/1.8)))

            if self.number:
                self.number_id = self.canvas.create_text(
                    self.x1+5*CELL_WIDTH//6, self.y1+CELL_HEIGHT//6,
                    text=self.number, font=("Arial", int(CELL_HEIGHT/3.5)))
            
        if self.type == BLACK_CELL:
            self.canvas.create_rectangle(self.x1, self.y1, self.x2, self.y2,
                                         fill="black")

class Word:
    """Playable crossword word."""

    def __init__(self, word, cells):
        self.word = word
        self.cells = cells

class Board:
    """Basic interpretation of the puz crossword board."""

    def __init__(self, width, height):
        """Initialize a new crossword board."""
        self.cells = []
        for y in range(height):
            self.cells.append(list())
            for x in range(width):
                self.cells[y].append(" ")

        self.selected = ()

    def set_selected(self, x, y):
        """Set the selected square."""
        for row in self.cells:
            for cell in row:
                if cell.selected:
                    cell.selected = False
                    cell.draw()
        self.cells[y][x].selected = True
        self.cells[y][x].draw()

        self.selected = (x, y)

    def __setitem__(self, position, value):
        """Board[x, y] = value"""
        self.cells[position[1]][position[0]] = value
    
    def __getitem__(self, position):
        """Board[x, y]"""
        return self.cells[position[1]][position[0]]
    
class Game:
    """Crossword game."""

    def __init__(self):
        pass

    def build(self):
        """Build the graphical interface for the game."""
        self.window = tkinter.Tk()
        self.window.resizable(False, False)
        self.window.title("New York Times Crossword")

        self.canvas = tkinter.Canvas(self.window, width=500, height=500)
        self.canvas.pack(side="left", fill="y")
        self.listbox = tkinter.Listbox(self.window)
        self.listbox.pack(side="right", fill="y")

        self.canvas.bind("<Button-1>", self.click)
        self.window.bind_all("<Key>", self.key)

        self.selection = [0, 0]

    def load(self, puzzle):
        """Setup the game with a puzzle object."""
        self.puzzle = puzzle
        self.board = Board(self.puzzle.width, self.puzzle.height)
        self.canvas.config(
            width=self.puzzle.width*(CELL_WIDTH+1) + CANVAS_MARGIN_OUTER,
            height=self.puzzle.height*(CELL_HEIGHT+1) + CANVAS_MARGIN_OUTER
        )
        self.canvas.create_rectangle(
            CANVAS_MARGIN_INNER-1, CANVAS_MARGIN_INNER-1,
            int(self.canvas.cget("width")),
            int(self.canvas.cget("height")),
        )

        numbering = self.puzzle.clue_numbering()
        numbers = {w["cell"]: w["num"] for w in numbering.across}
        numbers.update({w["cell"]: w["num"] for w in numbering.down})
        
        for y in range(self.puzzle.height):
            for x in range(self.puzzle.width):
                cell = Cell(
                    self.canvas,
                    self.puzzle.fill[y*self.puzzle.height + x],
                    CANVAS_MARGIN_INNER + x*CELL_WIDTH + x,
                    CANVAS_MARGIN_INNER + y*CELL_HEIGHT + y,
                    CANVAS_MARGIN_INNER + (x+1)*CELL_WIDTH + x,
                    CANVAS_MARGIN_INNER + (y+1)*CELL_HEIGHT + y,
                    number=numbers.get(y*self.puzzle.height + x, "")
                )
                self.board[x, y] = cell
                cell.draw()

        self.board.set_selected(0, 0)

    def click(self, event):
        """On click event for the crossword puzzle."""
        x = (event.x - CANVAS_MARGIN_INNER - 1) // (CELL_WIDTH + 1)
        y = (event.y - CANVAS_MARGIN_INNER - 1) // (CELL_HEIGHT + 1)
        self.board.set_selected(x, y)

    def key(self, event):
        """On key event for the crossword puzzle."""
        if event.char in string.ascii_letters + " ":
            x, y = self.board.selected
            self.board[x, y].letter = event.char.capitalize()
            self.board[x, y].draw()
           
        else:
            x, y = self.board.selected
            if event.keysym == "Up":
                y = (y-1) % self.puzzle.height
                while self.board[x, y].type == BLACK_CELL:
                    y = (y-1) % self.puzzle.height
                self.board.set_selected(x, y)
            if event.keysym == "Down":
                y = (y+1) % self.puzzle.height
                while self.board[x, y].type == BLACK_CELL:
                    y = (y+1) % self.puzzle.height
                self.board.set_selected(x, y)
            if event.keysym == "Left":
                x = (x-1) % self.puzzle.height
                while self.board[x, y].type == BLACK_CELL:
                    x = (x-1) % self.puzzle.height
                self.board.set_selected(x, y)
            if event.keysym == "Right":
                x = (x+1) % self.puzzle.height
                while self.board[x, y].type == BLACK_CELL:
                    x = (x+1) % self.puzzle.height
                self.board.set_selected(x, y)
                

                                    
g = Game()
g.build()
p = puz.read("Nov0705.puz")
g.load(p)
