# Crossword
# Noah Kim, Jordan Schneider

# Import
import logging
import time
import socket
import tkinter
import string

import puz

# Logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATEFMT = "%m/%d/%y %I:%M:%S %p"
LEVEL = NOTSET
logging.basicConfig(format=FORMAT, datefmt=DATEFMT, level=LEVEL)

# Constant
CHAT_MESSAGE = "chat"
GAME_MESSAGE = "game"
INFO_MESSAGE = "info"

IP = socket.gethostbyname(socket.gethostname())
PORT = 50000
SIZE = 1024

MARGIN = 3

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

LABEL_FONT = ("TkDefaultFont", 14, "bold")
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
            for x in range(self.puzzle.width):
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

class CrosswordPlayer:
    """A crossword game player that can connect to a host over a local network
    to play with other people."""

    def __init__(self):
        """Initialize a new crossword player."""
        self.alive = False

    def __repr__(self):
        """Generate a string representation of this crossword player."""
        return "CrosswordPlayer"

    def build(self):
        """Build the main graphical interface for the crossword game."""
        self.window = tkinter.Tk()
        self.window.resizable(False, False)
        self.window.title("New York Times Crossword")

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(fill="both", padx=MARGIN, pady=MARGIN)
        
        self.canvas = tkinter.Canvas(self.frame, bg="red")
        self.canvas.config(width=500, height=500)
        self.canvas.pack(side="left", fill="y")

        self.across_frame = tkinter.Frame(self.frame)
        self.across_frame.pack(side="right", fill="y", padx=MARGIN, pady=MARGIN)

        self.across_label = tkinter.Label(self.across_frame)
        self.across_label.config(text="Across", anchor="w", font=LABEL_FONT)
        self.across_label.pack(side="top", fill="x")

        self.across_listbox = tkinter.Listbox(self.across_frame)
        self.across_listbox.pack(fill="y")
    
        self.down_frame = tkinter.Frame(self.frame)
        self.down_frame.pack(side="right", fill="y", padx=MARGIN, pady=MARGIN)

        logging.log(DEBUG, "%s: build", repr(self))

    def unbuild(self):
        """Destroy the graphical interface."""
        self.window.destroy()
        self.window.quit()
        logging.log(DEBUG, "%s: unbuilt", repr(self))

    def load(self, puzzle):
        """Load a New York Times crossword puzzle."""
        self.puzzle = puzzle
        self.board = CrosswordBoard(self.puzzle)
        
        width = self.puzzle.width*(CELL_WIDTH+1) + MARGIN
        height = self.puzzle.height*(CELL_HEIGHT+1) + MARGIN
        self.canvas.config(width=width, height=height)
        self.canvas.create_rectangle(MARGIN, MARGIN, width, height)

        numbering = self.puzzle.clue_numbering()
        clues = numbering.across + numbering.down
"""
        for clue in numbering.across:
            self.across_listbox.insert("end", " %(num)i. %(clue)s" % clue)
        for clue in numbering.down:
            self.down_listbox.insert("end", " %(num)i. %(clue)s" % clue)        
        numbers = {w["cell"]: w["num"] for w in clues}
"""
class CrosswordHost(CrosswordPlayer):
    """A crossword game host that can be connected to over local network and
    uses NYTimes crossword puzzles."""

    def __init__(self):
        """Initialize a new crossword game host on the local address."""
        self.address = (IP, PORT)
        self.messages = queue.Queue()
        self.handlers = list()
        self.active = False
        logging.log(DEBUG, "%s: initialized", repr(self))

    def __repr__(self):
        """Generate a string representation of the crossword host."""
        return "Server()"

    def setup(self):
        """Set up the crossword host with a puzzle."""
        pass

    def send(self, message, handler=None):
        """Broadcast a message or send it to a specific handler."""
        if handler:
            handler.send(message)
        else:
            for handler in self.handlers:
                handler.send(message)

    def listen(self):
        """Listen for incoming connections from possible clients."""        
        logging.log(DEBUG, "%s: listen loop started", repr(self))
        while self.active:
            try:
                socket, address = self.socket.accept()
                handler = Handler(socket, address, self)
                handler.activate()
            except Exception as e:
                if self.active:
                    logging.log(ERROR, "%s: %s in listen", repr(self), name(e))

    def serve(self):
        """Main server loop handles incoming messages and handles them."""
        logging.log(DEBUG, "%s: serve loop started", repr(self))
        while self.active:
            try:
                while not self.messages.empty():
                    message = self.messages.get()
                    formatted = string(message["format"], message)
                    message = new(message=formatted)
                    self.send(message)
            except Exception as e:
                if self.active:
                    logging.log(ERROR, "%s: %s in serve", repr(self), name(e))

    def activate(self):
        """Activate the handler."""
        if self.active:
            logging.log(WARNING, "%s: already actvated", repr(self))
        try:
            self.socket = socket.socket()
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind(self.address)
            self.socket.listen(5)
            logging.log(DEBUG, "%s: bound" % repr(self))
        except OSError as e:
            logging.log(FATAL, "%s: could not bind" % repr(self))
            return
        logging.log(DEBUG, "%s: initialized" % repr(self))

class CrosswordPlayerHandler:
    """A crossword host player handler. Acts a middleman between the host and
    the connected player."""

    def __init__(self):
        pass

cp = CrosswordPlayer()
cp.build()
cp.load(puz.read("puzzles/Nov0705.puz"))
