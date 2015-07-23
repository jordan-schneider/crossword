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
        self.clues = ViewClues(self.root, self.frame)
        self.chat = type("chat", (), {})

    def setup(self):
        """Set graphical options to their defaults and bind events."""
        self.header.title.set("Hello, world!")
        self.header.author.set("Noah Kim")
        self.crossword.clue.set("This is a clue")
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
        self.frame = tk.Frame(self.parent)
        self.frame.grid(row=0, column=0, columnspan=4, padx=PAD, pady=PAD, sticky=tk.W+tk.E)
        self.frame.columnconfigure(0, weight=1)
        # Title of the crossword puzzle
        self.title = tk.StringVar(self.root)
        self.title_label = tk.Label(self.frame, textvariable=self.title)
        self.title_label.config(**settings.get("style:title"))
        self.title_label.grid(row=0, column=0, padx=EXTRA_PAD, pady=(0, PAD), sticky=tk.W)
        # Author of the crossword puzzle
        self.author = tk.StringVar(self.root)
        self.author_label = tk.Label(self.frame, textvariable=self.author)
        self.author_label.config(**settings.get("style:author"))
        self.author_label.grid(row=0, column=0, padx=EXTRA_PAD, pady=(0, PAD), sticky=tk.E)
        # Dividing line separating the header and the rest of the application
        self.separator = tk.Frame(self.frame)
        self.separator.config(height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR)
        self.separator.grid(row=1, padx=EXTRA_PAD, sticky=tk.W+tk.E)


class ViewCrossword:
    """The crossword group of the crossword application."""

    def __init__(self, root, parent):
        """Build the crossword widget group."""
        self.root = root
        self.parent = parent
        # Padding frame
        self.frame = tk.Frame(self.parent)
        self.frame.grid(row=1, column=0, padx=PAD, pady=0)
        # Crossword clue
        self.clue = tk.StringVar(self.root)
        self.clue_label = tk.Label(self.frame, textvariable=self.clue)
        self.clue_label.config(**settings.get("style:clue"))
        self.clue_label.grid(row=0, padx=EXTRA_PAD, sticky=tk.W)
        # Game timer
        self.time = tk.StringVar(self.root)
        self.time_label = tk.Label(self.frame, textvariable=self.time)
        self.time_label.config(**settings.get("style:time"))
        self.time_label.grid(row=0, padx=EXTRA_PAD, sticky=tk.E)
        # Game canvas
        canvas_width = settings.get("board:cell-size")*DEFAULT_PUZZLE_WIDTH + CANVAS_SPARE
        canvas_height = settings.get("board:cell-size")*DEFAULT_PUZZLE_HEIGHT + CANVAS_SPARE
        border_fill = settings.get("style:border:fill")
        self.canvas = tk.Canvas(self.frame)
        self.canvas.config(width=canvas_width, height=canvas_height, highlightthickness=0)
        self.canvas.grid(row=1, pady=PAD-1, padx=PAD-CANVAS_OFFSET)
        self.canvas.create_rectangle(0, 0, canvas_width-CANVAS_SPARE, canvas_height-CANVAS_SPARE, outline=border_fill)


class ViewClues:
    """The clues group of the crossword application."""

    def __init__(self, root, parent):
        """Build the clues widget group."""
        self.root = root
        self.parent = parent
        # Padding frame
        self.frame = tk.Frame(self.parent)
        self.frame.grid(row=1, column=1, padx=(EXTRA_PAD, PAD+EXTRA_PAD), pady=(0, PAD+EXTRA_PAD), sticky=tk.N+tk.S)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=1)
        # Across label
        self.across_label = tk.Label(self.frame)
        self.across_label.config(text="Across", anchor=tk.W, **settings.get("style:clue"))
        self.across_label.grid(row=0, column=0, sticky=tk.N+tk.W)
        # Across frame
        self.across = tk.Frame(self.frame)
        self.across.config(highlightthickness=1, highlightbackground=settings.get("style:border:fill"))
        self.across.grid(row=1, pady=(PAD-1, EXTRA_PAD), sticky=tk.N+tk.S)
        self.across.rowconfigure(0, weight=1)
        # Across list
        self.across_clues = tk.StringVar(self.root)
        self.across_listbox = tk.Listbox(self.across, listvariable=self.across_clues)
        self.across_listbox.config(bd=0, selectborderwidth=0, **settings.get("style:list"))
        self.across_listbox.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.across_scrollbar = tk.Scrollbar(self.across)
        self.across_scrollbar.config(command=self.across_listbox.yview)
        self.across_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.across_listbox.config(yscrollcommand=self.across_scrollbar.set)
        # Down Label
        self.down_label = tk.Label(self.frame)
        self.down_label.config(text="Down", anchor=tk.W, **settings.get("style:clue"))
        self.down_label.grid(row=2, column=0, pady=(PAD, 0), sticky=tk.N+tk.W)
        # Down frame
        self.down = tk.Frame(self.frame)
        self.down.config(highlightthickness=1, highlightbackground=settings.get("style:border:fill"))
        self.down.grid(row=3, pady=(EXTRA_PAD, 0), sticky=tk.N+tk.S)
        self.down.rowconfigure(0, weight=1)
        # Down list
        self.down_clues = tk.StringVar(self.root)
        self.down_listbox = tk.Listbox(self.down)
        self.down_listbox.config(bd=0, selectborderwidth=0, **settings.get("style:list"))
        self.down_listbox.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.down_scrollbar = tk.Scrollbar(self.down)
        self.down_scrollbar.config(command=self.down_listbox.yview)
        self.down_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.down_listbox.config(yscrollcommand=self.down_scrollbar.set)
