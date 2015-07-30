"""The Main Crossword Application Interface.

View serves as the graphical component in crossword. Instantiating a
`View` object spawns and loads a new crossword application. This
application must be the main thread, as tkinter is not thread-safe.
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
        self.header = HeaderView(self)
        self.puzzle = PuzzleView(self)
        self.clues = CluesView(self)
        # Show widgets
        self.header.show()
        self.puzzle.show()
        self.clues.show()

    def main(self):
        """Run the main loop of the view."""
        self.root.mainloop()

    def stop(self):
        """Stop the view during the main loop."""
        self.root.quit()


class SubView:
    """Parent class for a crossword application widget group."""

    def __init__(self, parent: View):
        """Build the widget group."""
        self.parent = parent
        self.root = self.parent.root
        # Content frame
        self.frame = tk.Frame(self.parent.frame)
        # Reference
        self.visible = False

    def load(self):
        """Load the graphical components of the group."""
        pass

    def show(self):
        """Show the widget in its parent."""
        self.frame.grid()
        self.visible = True

    def hide(self):
        """Hide the widget in its parent."""
        self.frame.grid_forget()
        self.visible = False


class HeaderView(SubView):
    """The header group of the crossword application."""

    def __init__(self, parent: View):
        """Build the header widget group."""
        super().__init__(parent)
        # Crossword title
        self.title = tk.StringVar(self.root)
        self.title_label = tk.Label(self.frame, textvariable=self.title)
        # Crossword author
        self.author = tk.StringVar(self.root)
        self.author_label = tk.Label(self.frame, textvariable=self.author)
        # Dividing line separating the header and other groups
        self.separator = tk.Frame(self.frame)
        # Load
        self.load()

    def load(self):
        """Load the graphical components of the group."""
        # Frame
        self.frame.grid_configure(row=0, column=0, columnspan=4, padx=PAD, pady=(TINY_PAD, PAD), sticky=tk.W+tk.E)
        self.frame.columnconfigure(0, weight=1)
        # Crossword title
        self.title_label.config(**settings.get("style:title"))
        self.title_label.grid(row=0, column=0, pady=(0, PAD), sticky=tk.W)
        # Crossword author
        self.author_label.config(**settings.get("style:author"))
        self.author_label.grid(row=0, column=0, padx=TINY_PAD, pady=(0, PAD), sticky=tk.E)
        # Separator
        self.separator.config(height=SEPARATOR_HEIGHT, bg=SEPARATOR_COLOR)
        self.separator.grid(row=1, padx=TINY_PAD, sticky=tk.W+tk.E)


class PuzzleView(SubView):
    """The puzzle group of the crossword application."""

    def __init__(self, parent: View):
        """Build the crossword widget group."""
        super().__init__(parent)
        # Crossword clue
        self.clue = tk.StringVar(self.root)
        self.clue_label = tk.Label(self.frame, textvariable=self.clue)
        # Game timer
        self.time = tk.StringVar(self.root)
        self.time_label = tk.Label(self.frame, textvariable=self.time)
        # Game canvas
        self.canvas = tk.Canvas(self.frame)
        # Load
        self.load()

    def load(self, width=DEFAULT_PUZZLE_WIDTH, height=DEFAULT_PUZZLE_HEIGHT):
        """Load the graphical components of the group."""
        self.frame.grid_configure(row=1, column=0, padx=PAD, pady=0)
        # Crossword clue
        self.clue_label.config(**settings.get("style:clue"))
        self.clue_label.grid(row=0, sticky=tk.W)
        # Game timer
        self.time_label.config(**settings.get("style:time"))
        self.time_label.grid(row=0, padx=TINY_PAD+1, sticky=tk.E)
        # Game canvas
        canvas_width = settings.get("board:cell-size")*width + CANVAS_SPARE
        canvas_height = settings.get("board:cell-size")*height + CANVAS_SPARE
        border_fill = settings.get("style:border:fill")
        self.canvas.config(width=canvas_width, height=canvas_height, highlightthickness=0)
        self.canvas.grid(row=1, pady=PAD, padx=(PAD-CANVAS_PAD, 0))
        self.canvas.create_rectangle(0, 0, canvas_width-CANVAS_SPARE, canvas_height-CANVAS_SPARE, outline=border_fill)


class CluesView(SubView):
    """The clues group of the crossword application."""

    def __init__(self, parent: View):
        """Build the clues widget group."""
        super().__init__(parent)
        # Across label
        self.across_label = tk.Label(self.frame)
        # Across frame
        self.across_frame = tk.Frame(self.frame)
        # Across list and scrollbar
        self.across = CustomListbox(self.across_frame)
        self.across_scrollbar = tk.Scrollbar(self.across_frame)
        # Down Label
        self.down_label = tk.Label(self.frame)
        # Down frame
        self.down_frame = tk.Frame(self.frame)
        # Down list and scrollbar
        self.down = CustomListbox(self.down_frame)
        self.down_scrollbar = tk.Scrollbar(self.down_frame)
        # Load
        self.load()

    def load(self):
        """Load the graphical components of the group."""
        # Frame
        self.frame.grid_configure(row=1, column=1, padx=(PAD, PAD+TINY_PAD), pady=(0, PAD+CANVAS_PAD), sticky=tk.N+tk.S)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=1)
        # Across label
        self.across_label.config(text="Across", anchor=tk.W, **settings.get("style:clue"))
        self.across_label.grid(row=0, column=0, pady=(0, TINY_PAD), sticky=tk.N+tk.W)
        # Across frame
        self.across_frame.config(highlightthickness=1, highlightbackground=settings.get("style:border:fill"))
        self.across_frame.grid(row=1, pady=(CANVAS_PAD, PAD), sticky=tk.N+tk.S)
        self.across_frame.rowconfigure(0, weight=1)
        # Across listbox
        self.across.config(bd=0, selectborderwidth=0, **settings.get("style:list"))
        self.across.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.across.config(yscrollcommand=self.across_scrollbar.set)
        # Across scrollbar
        self.across_scrollbar.config(command=self.across.yview)
        self.across_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        # Down label
        self.down_label.config(text="Down", anchor=tk.W, **settings.get("style:clue"))
        self.down_label.grid(row=2, column=0, pady=(PAD, 0), sticky=tk.N+tk.W)
        # Down frame
        self.down_frame.config(highlightthickness=1, highlightbackground=settings.get("style:border:fill"))
        self.down_frame.grid(row=3, pady=(TINY_PAD, 0), sticky=tk.N+tk.S)
        self.down_frame.rowconfigure(0, weight=1)
        # Down listbox
        self.down.config(bd=0, selectborderwidth=0, **settings.get("style:list"))
        self.down.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.down.config(yscrollcommand=self.down_scrollbar.set)
        # Down scrollbar
        self.down_scrollbar.config(command=self.down.yview)
        self.down_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)


class CustomListbox(tk.Listbox):

    def clear(self):
        self.delete("0", tk.END)

    def set(self, values):
        self.clear()
        for value in values:
            self.insert(tk.END, value)
