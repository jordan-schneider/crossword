import collections
from crossword.application import model


class PlayerMetrics:
    """A simple container object for player statistics."""

    def __init__(self, name, color):
        """Initialize a crossword metrics model with a name and color."""
        self.name = name
        self.color = color
        # Crossword letters
        self.letters_total = 0
        self.letters_replaced = 0
        self.letters_final = 0
        # Chat data
        self.chat_entries = 0
        self.chat_words = 0
        self.chat_letters = 0
        self.chat_word_frequency = collections.Counter()


class PuzzleMetrics:
    """A simple container object for game statistics."""

    def __init__(self, puzzle: model.PuzzleModel):
        """Initialize a crossword metrics model."""
        self.author = puzzle.author
        self.width = puzzle.width
        self.height = puzzle.height
        self.cells = len(puzzle.cells)
        self.words = len(puzzle.words)
        # Timing
        self.time_start = 0
        self.time_finish = 0
        self.time_fill = 0
        self.time_total = 0
        # Players
        self.player_list = []
