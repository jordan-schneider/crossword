import collections


class PlayerMetrics:
    """A simple container object for player statistics."""

    def __init__(self, name, color):
        """Initialize a new metrics model with a name and color."""
        self.name = name
        self.color = color
        # Crossword letters
        self.letters_total = 0
        self.letters_final = 0
        # Chat data
        self.chat_entries = 0
        self.chat_words = 0
        self.chat_letters = 0
        self.chat_word_frequency = collections.Counter()


class PuzzleMetrics:
    """A simple container object for game statistics."""

    def __init__(self, author, width, height, cells, words):
        """Initialize a new metrics model."""
        self.author = author
        self.width = width
        self.height = height
        self.cells = cells
        self.words = words
        # Timing
        self.time_start = 0
        self.time_finish = 0
        self.time_fill = 0
        self.time_total = 0
        # Players
        self.player_list = []