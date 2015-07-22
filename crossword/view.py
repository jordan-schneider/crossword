"""The Main Crossword Application Interface.

Use `view.get()` to initialize, build, and return a new crossword
application. The application must be the main thread, as tkinter is
not thread-safe.
"""


# Data
__author__ = "Noah Kim"
__version__ = "0.2.0"
__status__ = "Development"


# Import
import tkinter as tk
from .constants import *


# Application
class View:
    """The main crossword application interface."""

    def __init__(self):
        """Initialize a new crossword application."""
        # Root window
        self.root = tk.Tk()
        self.root.title("Crossword")
        # Padding frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", padx=PAD, pady=PAD)
        # Initialize widget groups
        self.header = ViewHeader(self.root, self.frame)
        self.crossword = type("crossword", (), {})
        self.clues = type("clues", (), {})
        self.chat = type("chat", (), {})


class ViewHeader:
    """The header group of the crossword application."""

    def __init__(self, root, parent):
        """Build the header widget group."""
        # Padding frame
        self.frame = tk.Frame(parent)
        self.frame.grid(row=0, column=0, columnspan=3, padx=PAD, pady=PAD)
        # Title of the crossword puzzle
        self.title = tk.StringVar(root)
        self.title_label = tk.Label(self.frame, variable=self.title)
        self.title_label.grid(row=0, sticky=tk.W)
        # Author of the crossword puzzle
        self.author = tk.StringVar(root)
        self.author_label = tk.Label(self.frame, variable=self.author)
        self.author_label.grid(row=0, sticky=tk.E)
        # Dividing line separating the header and the rest of the application
        self.separator = tk.Frame(self.frame)
        self.separator.config(height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR)
        self.separator.grid(row=1, sticky=tk.W+tk.E)


class ViewCrossword:
    """The crossword group of the crossword application."""

    def __init__(self, root, parent):
        """Build the crossword widget group."""
        # Padding frame
        self.frame = tk.Frame(parent)
        self.frame.grid(row=0, column=1, padx=PAD, pady=PAD)
        # Crossword hint
        self.hint = tk.StringVar(root)
        self.hint_label = tk.Label(self.frame, variable=self.hint)
        self.hint_label.grid(row=0, column=0, sticky=tk.W)
        # Game timer
        self.time = tk.StringVar(root)
        self.time_label = tk.Label(self.frame, variable=self.time)
        self.time_label.grid(row=0, column=0, sticky=tk.E)
        # Game canvas
        self.canvas = tk.Canvas(self.frame)
        self.canvas.config()