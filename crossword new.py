# Crossword
# Noah Kim, Jordan Schneider

# Import
import time
import socket
import tkinter
import string

import puz

# Constant
CHAT_MESSAGE = "chat"
GAME_MESSAGE = "game"
INFO_MESSAGE = "info"

CANVAS_MARGIN = 6

CELL_WIDTH = 35
CELL_HEIGHT = 35
CELL_LETTER_FONT = ("TkDefaultFont", int(CELL_HEIGHT / 1.8))
CELL_NUMBER_FONT = ("TkDefaultFont", int(CELL_HEIGHT / 3.5))

CELL_TEXT_X = CELL_WIDTH//2
CELL_TEXT_Y = CELL_HEIGHT//2
CELL_NUMBER_X = 4*CELL_WIDTH//5
CELL_NUMBER_Y = CELL_HEIGHT//5

LETTER_CELL_FILL = "white"
LETTER_CELL_SFILL = "grey85"
EMPTY_CELL_FILL = "black"

TEXT_FONT = ("TkDefaultFont", 13)

LETTER_CELL = "-"
EMPTY_CELL = "."

# Crossword
class CrosswordCell:
    """Single crossword puzzle cell. Can be either an interactable letter cell
    or a non-interactable empty cell. If it is a letter cell it will draw the
    letter in the center and the number in the top right corner on the given
    canvas."""

    def __init__(self, canvas, celltype, x, y, letter="", number=""):
        """Initialize a new crossword puzzle cell."""
        self.canvas = canvas
        self.celltype = celltype
        self.x = x
        self.y = y
        self.letter = letter
        self.number = number

        self.selected = False
        self.drawings = [0]

    def draw(self):
        """Draw the cell and its contents onto the given canvas."""
        self.canvas.delete(*self.drawings)
        if self.celltype == LETTER_CELL:
            position = (self.x, self.y, self.x+CELL_WIDTH, self.y+CELL_HEIGHT)
            text_position = (self.x+CELL_TEXT_X, self.y+CELL_TEXT_Y)
            number_position = (self.x+CELL_NUMBER_X, self.y+CELL_NUMBER_Y)
            fill = LETTER_CELL_SFILL if self.selected else LETTER_CELL_FILL

            cell = self.canvas.create_rectangle(*position, fill=fill)
            letter = self.canvas.create_text(
                *text_position, text=self.letter, font=CELL_LETTER_FONT)
            self.drawings = [cell, letter]
            if self.number:
                number = self.canvas.create_text(
                    *number_position, text=self.number, font=CELL_NUMBER_FONT)
                self.drawings.append(number)

        else:
            position = (self.x, self.y, self.x+CELL_WIDTH, self.y+CELL_HEIGHT)
            fill = EMPTY_CELL_FILL
            
            cell = self.canvas.create_rectangle(*position, fill=fill)
            self.drawings = [cell]

class CrosswordBoard:
    """A basic container class for a crossword board. Initialized with a puz
    crossword puzzle."""

    def __init__(self, puzzle):
        """Initialize a new crossword board."""
        self.puzzle = puzzle

        self.cells = []
        self.selected = ()
        for y in range(self.puzzle.height):
            self.cells.append(list())
            for x in range(width):
                self.cells[y].append("")

    def __setitem__(self, position, value):
        """Set values of the board with 2D indexing."""
        self.cells[position[1]][position[0]] = value

    def __getitem__(self, position):
        """Get values of the board with 2D indexing."""
        return self.cells[position[1]][position[0]]

    def select(self, x, y):
        """Set a certain cell as selected and redraw it. Also redraws the
        previously selected cell."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[self.selected[0], self.selected[1]].selected = False
            self.cells[self.selected[0], self.selected[1]].draw()            
            self.cells[x, y].selected = True
            self.cells[x, y].draw()

class CrosswordHost:
    """A crossword game host that can be connected to over local network and
    uses NYTimes crossword puzzles."""

    def __init__(self):
        """Initialize a new crossword host."""
        self.address = (socket.gethostbyname(socket.gethostname()), 50000)
        self.messages = queue.Queue()
        self.handlers =  list()
        self.alive = False

    def __repr__(self):
        """Generate a string that represents this object."""
        return "Server@%s" % self.address[0]

    def send(self, message, handler=None):
        """Broadcast a message or send it to only a specific handler."""
        if handler:
            self.handler.send(message)
        else:
            for handler in self.handlers:
                handler.send(message)
        logging.log(INFO, "%s: sent message", repr(self))

    def listen(self):
        """List for incoming connections from possible clients."""
        logging.log(DEBUG, "%s: listen loop started", repr(self))
        while self.active:
            try:
                socket, address = self.socket.accept()
                handler = Handler(socket, address, self)
                handler.activate()
            except Exception as e:
                if self.active:
                    logging.log(ERROR, "%s: %s in listen", repr(self), name(e))

class CrosswordPlayerHandler:
    """A crossword host player handler. Acts a middleman between the host and
    the connected player."""

    def __init__(self):
        pass

class CrosswordPlayer:
    """A crossword game player that can connect to a host over a local network
    to play with other people."""

    def __init__(self):
        pass

