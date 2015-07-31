import puz
from .constants import *


class CellModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, x: int, y: int, kind: str, solution: str):
        """Initialize a new cell container."""
        # Set by fill and solution
        self.x = x
        self.y = y
        self.kind = kind
        self.across = None
        self.down = None
        self.solution = solution
        # Changeable
        self.letters = ""
        self.owner = None
        # Constant
        self.number = ""
        self.fill = "white"
        # Drawing
        self.drawings = type("CellDrawing", (), {})
        self.drawings.box = None
        self.drawings.number = None
        self.drawings.letter = None

    @property
    def color(self):
        return "" if not self.owner else self.owner.color


class CellsModel:
    """Basic matrix-like container for a crossword board's cells."""

    def __init__(self, puzzle: puz.Puzzle):
        """Initialize a new cells container."""
        self._width = puzzle.width
        self.cells = []
        zipped = list(zip(puzzle.fill, puzzle.solution))
        for y, row in enumerate(zipped[i:i+puzzle.width] for i in range(0, len(zipped), puzzle.width)):
            for x, (kind, solution) in enumerate(row):
                self.cells.append(CellModel(x, y, kind, solution))

    def __getitem__(self, position: (int, tuple)):
        """Get a cell with its coordinate position."""
        if isinstance(position, int):
            return self.cells[position]
        elif isinstance(position, tuple) and len(position) == 2:
            return self.cells[to_index(position[1], position[0], self._width)]

    def __iter__(self):
        return iter(self.cells)


class WordModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, direction: str, number: int, clue: int):
        """Initialize a new cell container."""
        # Basic word data
        self.direction = direction
        self.number = number
        self.clue = clue
        self.cells = []

    @property
    def fill(self):
        return None

    @fill.setter
    def fill(self, value):
        for cell in self.cells:
            cell.fill = value


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
            linked = list(map(lambda j: cells[x+j, y], range(info["len"])))
            word = WordModel(ACROSS, info["num"], info["clue"])
            # Link the word and cells
            word.cells = linked
            for cell in linked:
                cell.across = word
            word.cells[0].number = word.number
            # Add the word to the lists
            self.words.append(word)
            self.across.append(word)
        for info in numbering.down:
            x, y = to_position(info["cell"], puzzle.width)
            linked = list(map(lambda j: cells[x, y+j], range(info["len"])))
            word = WordModel(DOWN, info["num"], info["clue"])
            # Link the word and cells
            word.cells = linked
            for cell in linked:
                cell.down = word
            word.cells[0].number = word.number
            # Add the word to the lists
            self.words.append(word)
            self.down.append(word)

    def __iter__(self):
        return self.words


class PuzzleModel:
    """Basic container class for a single crossword cell."""

    def __init__(self, puzzle: puz.Puzzle):
        """Initialize a new cell container with a puzzle."""
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

    def __init__(self, name: str, color: str):
        """Initialize a player profile model."""
        self.name = name
        self.color = color

