import puz
from .constants import *


def to_position(i, w):
    y, x = divmod(i, w)
    return x-1, y


def to_index(x, y, w):
    return y*w + x+1


class CellModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, x, y, kind, solution):
        """Initialize a new cell container."""
        # Set by fill and solution
        self.x = x
        self.y = y
        self.kind = kind
        self.solution = solution
        # Set later on
        self.letters = ""
        self.number = ""
        self.owner = None
        self.fill = ""


class WordModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, direction, number, clue, cells):
        """Initialize a new cell container."""
        # Basic word data
        self.direction = direction
        self.number = number
        self.clue = clue
        self.cells = cells
        # Set the cell number
        self.cells[0].number = str(self.number)


class PuzzleModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, puzzle):
        """Initialize a new cell container."""
        # Basic puzzle data
        self.title = puzzle.title
        self.author = puzzle.author
        self.copyright = puzzle.copyright
        self.notes = puzzle.notes
        self.postscript = puzzle.postscript
        self.width = puzzle.width
        self.height = puzzle.height
        self.version = puzzle.version
        # Cells and words
        self.cells = []
        self.words = []

        # Cell generation
        for i, (kind, solution) in enumerate(zip(puzzle.fill, puzzle.solution)):
            x, y = to_position(i, puzzle.width)
            self.cells.append(CellModel(x, y, kind, solution))
        # Word generation
        numbering = puzzle.get_numbering()
        for info in numbering.across:
            x, y = to_position(info["cell"], self.width)
            cells = list(map(lambda j: self[x+j, y], range(info["len"])))
            self.words.append(WordModel(ACROSS, info["num"], info["clue"], cells))
        for info in numbering.down:
            x, y = to_position(info["cell"], self.width)
            cells = list(map(lambda j: self[x, y+j], range(info["len"])))
            self.words.append(WordModel(DOWN, info["num"], info["clue"], cells))

    def __getitem__(self, position):
        """Get a cell based on its coordinate position."""
        return self.cells[position[1]][position[0]]


class ProfileModel:
    """Basic player profile model for use on the client side."""

    def __init__(self, name, color):
        """Initialize a player profile model."""
        self.name = name
        self.color = color
