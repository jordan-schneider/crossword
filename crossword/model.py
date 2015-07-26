import puz
from .constants import *


def to_position(i: int, w: int) -> tuple:
    y, x = divmod(i, w)
    return x-1, y


def to_index(x: int, y: int, w: int) -> int:
    return y*w + x+1


class CellModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, x: int, y: int, kind: str, solution: str):
        """Initialize a new cell container."""
        # Set by fill and solution
        self.x = x
        self.y = y
        self.kind = kind
        self.word = None
        self.solution = solution
        # Set later on
        self.letters = ""
        self.number = ""
        self.owner = None
        self.fill = ""


class CellsModel:
    """Basic matrix-like container for a crossword board's cells."""

    def __init__(self, puzzle: puz.Puzzle):
        """Initialize a new cells container."""
        self.cells = []
        for i, (kind, solution) in enumerate(zip(puzzle.fill, puzzle.solution)):
            x, y = to_position(i, puzzle.width)
            self.cells.append(CellModel(x, y, kind, solution))

    def __getitem__(self, position: tuple):
        """Get a cell with its coordinate position."""
        return self.cells[position[1]][position[0]]


class WordModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, direction: str, number: int, clue: int):
        """Initialize a new cell container."""
        # Basic word data
        self.direction = direction
        self.number = number
        self.clue = clue
        self.cells = None


class WordsModel:
    """Basic container for a list of words."""

    def __init__(self, puzzle: puz.Puzzle, cells: CellsModel):
        """Initialize a new words container."""
        self.words = []
        self.across = []
        self.down = []
        # Load the words
        numbering = puzzle.clue_numbering()
        for info in numbering.across:
            x, y = to_position(info["cell"], puzzle.width)
            linked = list(map(lambda j: cells[x, y+j], range(info["len"])))
            word = WordModel(ACROSS, info["num"], info["clue"])
            # Link the word and cells
            word.cells = linked
            for cell in linked:
                cell.word = word
            # Add the word to the lists
            self.words.append(word)
            self.across.append(word)
        for info in numbering.down:
            x, y = to_position(info["cell"], puzzle.width)
            linked = list(map(lambda j: cells[x, y+j], range(info["len"])))
            word = WordModel(DOWN, info["number"], info["down"])
            # Link the word and cells
            word.cells = linked
            for cell in linked:
                cell.word = word
            # Add the word to the lists
            self.words.append(word)
            self.down.append(word)


class PuzzleModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, puzzle: puz.Puzzle):
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
        self.cells = CellsModel(puzzle)
        self.words = WordsModel(puzzle, self.cells)


class ProfileModel:
    """Basic player profile model for use on the client side."""

    def __init__(self, name, color):
        """Initialize a player profile model."""
        self.name = name
        self.color = color


class SelectionModel:
    """Controller selection container."""

    def __init__(self):
        """Initialize a selection container."""
        self.cell = None
        self.word = None

    def set(self, cell: CellModel):
