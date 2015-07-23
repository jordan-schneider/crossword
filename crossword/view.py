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
from . import settings
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
        self.crossword = ViewCrossword(self.root, self.frame)
        self.clues = type("clues", (), {})
        self.chat = type("chat", (), {})

    def setup(self):
        """Set graphical options to their defaults and bind events."""
        self.header.title.set("Hello, world!")
        self.header.author.set("Noah Kim")
        self.crossword.hint.set("This is a hint")
        self.crossword.time.set("00:00:00")

    def main(self):
        """Run the main loop of the view."""
        self.setup()
        self.root.mainloop()

    def stop(self):
        """Stop the view during the main loop."""
        self.root.quit()


class ViewHeader:
    """The header group of the crossword application."""

    def __init__(self, root, parent):
        """Build the header widget group."""
        self.root = root
        self.parent = parent
        # Padding frame
        self.frame = tk.Frame(parent, bg="red")
        self.frame.grid(row=0, column=0, columnspan=3, padx=PAD, pady=PAD, sticky=tk.W+tk.E)
        # Title of the crossword puzzle
        self.title = tk.StringVar(root)
        self.title_label = tk.Label(self.frame, textvariable=self.title)
        self.title_label.config(**settings.get("style:title"))
        self.title_label.grid(row=0, sticky=tk.W)
        # Author of the crossword puzzle
        self.author = tk.StringVar(root)
        self.author_label = tk.Label(self.frame, textvariable=self.author)
        self.author_label.config(**settings.get("style:header"))
        self.author_label.grid(row=0, sticky=tk.E)
        # Dividing line separating the header and the rest of the application
        self.separator = tk.Frame(self.frame)
        self.separator.config(height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR)
        self.separator.grid(row=1, sticky=tk.W+tk.E)


class ViewCrossword:
    """The crossword group of the crossword application."""

    def __init__(self, root, parent):
        """Build the crossword widget group."""
        self.root = root
        self.parent = parent
        # Padding frame
        self.frame = tk.Frame(parent)
        self.frame.grid(row=1, column=0, padx=PAD, pady=PAD)
        # Crossword hint
        self.hint = tk.StringVar(root)
        self.hint_label = tk.Label(self.frame, textvariable=self.hint)
        self.hint_label.config(**settings.get("style:label"))
        self.hint_label.grid(row=0, column=0, sticky=tk.W)
        # Game timer
        self.time = tk.StringVar(root)
        self.time_label = tk.Label(self.frame, textvariable=self.time)
        self.time_label.config(**settings.get("style:time"))
        self.time_label.grid(row=0, column=0, sticky=tk.E)
        # Game canvas
        canvas_width = settings.get("board:cell-size")*DEFAULT_PUZZLE_WIDTH + CANVAS_SPARE
        canvas_height = settings.get("board:cell-size")*DEFAULT_PUZZLE_HEIGHT + CANVAS_SPARE
        self.canvas = tk.Canvas(self.frame)
        self.canvas.config(width=canvas_width, height=canvas_height, highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=5-CANVAS_OFFSET)


class ViewClues:
    """The clues group of the crossword application."""

    def __init__(self, root, parent):
        """Build the clues widget group."""
        self.root = root
        self.parent = parent
        # Padding frame
        self.frame = tk.Frame(parent)
        self.frame.grid(row=1, column=1, padx=PAD, pady=PAD)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)
        # Across frame
        self.across = tk.Frame(self.frame)
        self.across.grid(row=0, column=0, padx=PAD, pady=PAD+EXTRA_PAD, sticky=tk.N+tk.S)
        self.across.rowconfigure(1, weight=1)
        # Across label
        self.across_label = tk.Frame(self.across)
        self.across_label.config(text="Across", anchor=tk.W, **settings.get("style:label"))
        self.across_label.grid(row=0, sticky="w")
        # Across list
        self.across_list = tk.Listbox(self.across)
        self.across_list.config(bd=0, selectborderwidth=0, **settings.get("style:list"))
