import tkinter as tk
import tkinter.filedialog as fd
from crossword.settings import settings
from crossword.constants import *

appearance = settings.appearance


# Application
class View:
    """The main old application interface.

    View has three main subviews, a header view, a puzzle view, and a
    clues view. There is also a chat view, which is loaded used for
    interaction in multiplayer.
    """

    def __init__(self):
        """Initialize a crossword old application."""
        # Root window
        self.root = tk.Tk()
        self.root.title("Crossword")
        # Padding frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(fill="both", padx=PAD, pady=PAD)
        # Initialize header widget
        self.header_frame = tk.Frame(self.frame)
        self.puzzle_frame = tk.Frame(self.frame)
        self.clues_frame = tk.Frame(self.frame)
        self.load()
        # Load each subview
        self.header = HeaderView(self, self.header_frame)
        self.puzzle = PuzzleView(self, self.puzzle_frame)
        self.clues = CluesView(self, self.clues_frame)
        # Show widgets
        self.header.show()
        self.puzzle.show()
        self.clues.show()
        logging.info("%s: started main view")

    def __repr__(self):
        return "view"

    def load(self):
        """Load the widgets of the view."""
        self.header_frame.grid_configure(row=0, column=0, columnspan=4, padx=PAD, pady=(TINY_PAD, PAD), sticky=tk.W+tk.E)
        self.header_frame.columnconfigure(0, weight=1)
        self.puzzle_frame.grid_configure(row=1, column=0, padx=PAD, pady=0)


    def hide(self):
        """Hide the entire view."""
        self.root.iconify()  # self.root.withdraw()

    def show(self):
        """Show the entire view."""
        self.root.update()
        self.root.deiconify()

    def main(self):
        """Run the main loop of the view."""
        self.root.mainloop()

    def stop(self):
        """Stop the view during the main loop."""
        self.root.quit()

    def call(self, event):
        """Call events from the view object."""
        self.root.event_generate(event, when="tail")


class SubView:
    """Parent class for a crossword application subview.

    Essentially a widget group namespace. Provides more convenient
    access to the important members of each subview.
    """

    def __init__(self, parent: View, frame: tk.Frame):
        """Build the widget group."""
        self.parent = parent
        self.root = self.parent.root
        # Content frame
        self.frame = frame
        # Reference
        self.visible = False

    def load(self):
        """Configure the graphical components of the group."""
        pass

    def show(self):
        """Show the widget in its parent."""
        self.frame.grid()
        self.visible = True

    def hide(self):
        """Hide the widget in its parent."""
        self.frame.grid_forget()
        self.visible = False

    def call(self, event):
        """Call events from the view object."""
        self.frame.event_generate(event, when="tail")


class HeaderView(SubView):
    """The header group of the crossword application."""

    def __init__(self, parent: View, frame: tk.Frame):
        """Build the header widget group."""
        super().__init__(parent, frame)
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
        """Configure the graphical components of the group."""
        # Crossword title
        title_style = {"font": appearance.header.font, "fg": appearance.header.title.fg}
        self.title_label.config(**title_style)
        self.title_label.grid(row=0, column=0, pady=(0, PAD), sticky=tk.W)
        # Crossword author
        author_style = {"font": appearance.header.font, "fg": appearance.header.author.fg}
        self.author_label.config(**author_style)
        self.author_label.grid(row=0, column=0, padx=TINY_PAD, pady=(0, PAD), sticky=tk.E)
        # Separator
        separator_style = dict(appearance.header.separator)
        self.separator.config(separator_style)
        self.separator.grid(row=1, padx=TINY_PAD, sticky=tk.W+tk.E)


class PuzzleView(SubView):
    """The puzzle group of the crossword application."""

    def __init__(self, parent: View, frame: tk.Frame):
        """Build the crossword widget group."""
        super().__init__(parent, frame)
        # Crossword clue
        self.clue = tk.StringVar(self.root)
        self.clue_label = tk.Label(self.frame, textvariable=self.clue)
        # Game timer
        self.time = tk.StringVar(self.root)
        self.time_label = tk.Label(self.frame, textvariable=self.time)
        # Game canvas
        self.canvas = tk.Canvas(self.frame)
        # Cells
        self.cells = None
        # Load
        self.load()

    def load(self, width=DEFAULT_PUZZLE_WIDTH, height=DEFAULT_PUZZLE_HEIGHT):
        """Configure the graphical components of the group."""
        # Crossword clue
        clue_style = dict(appearance.puzzle.clues)
        self.clue_label.config(**clue_style)
        self.clue_label.grid(row=0, sticky=tk.W)
        # Game timer
        time_style = dict(appearance.puzzle.time)
        self.time_label.config(**time_style)
        self.time_label.grid(row=0, padx=TINY_PAD+1, sticky=tk.E)
        # Game canvas
        canvas_width = appearance.puzzle.cell.size*width + CANVAS_PAD
        canvas_height = appearance.puzzle.cell.size*height + CANVAS_PAD
        border_fill = appearance.puzzle.fg
        self.canvas.config(width=canvas_width, height=canvas_height, highlightthickness=0)
        self.canvas.grid(row=1, pady=PAD, padx=(CANVAS_PAD_LEFT, 0))
        box_width = canvas_width - CANVAS_PAD
        box_height = canvas_height - CANVAS_PAD
        self.canvas.create_rectangle(0, 0, box_width, box_height, outline=border_fill)


class CluesView(SubView):
    """The clues group of the crossword application."""

    def __init__(self, parent: View, frame: tk.Frame):
        """Build the clues widget group."""
        super().__init__(parent, frame)
        # Across label
        self.across_label = tk.Label(self.frame)
        # Across frame
        self.across_frame = tk.Frame(self.frame)
        # Across list and scrollbar
        self.across_listbox = tk.Listbox(self.across_frame)
        self.across = ListVar(self.across_listbox)
        self.across_scrollbar = tk.Scrollbar(self.across_frame)
        # Down Label
        self.down_label = tk.Label(self.frame)
        # Down frame
        self.down_frame = tk.Frame(self.frame)
        # Down list and scrollbar
        self.down_listbox = tk.Listbox(self.down_frame)
        self.down = ListVar(self.down_listbox)
        self.down_scrollbar = tk.Scrollbar(self.down_frame)
        # Load
        self.load()

    def load(self):
        """Configure the graphical components of the group."""
        # Frame
        self.frame.grid_configure(row=1, column=1, padx=(PAD, PAD+TINY_PAD), pady=(0, PAD+CANVAS_PAD), sticky=tk.N+tk.S)
        self.frame.rowconfigure(1, weight=1)
        self.frame.rowconfigure(3, weight=1)
        # Across label
        clues_style = dict(appearance.clues)
        self.across_label.config(text="Across", anchor=tk.W, **clues_style)
        self.across_label.grid(row=0, column=0, pady=(0, TINY_PAD), sticky=tk.N+tk.W)
        # Across frame
        self.across_frame.config(highlightthickness=1, highlightbackground=appearance.clues.fg)
        self.across_frame.grid(row=1, pady=(CANVAS_PAD, PAD), sticky=tk.N+tk.S)
        self.across_frame.rowconfigure(0, weight=1)
        # Across listbox
        list_style = dict(appearance.clues.list)
        self.across_listbox.config(bd=0, selectborderwidth=0, activestyle=tk.NONE, **list_style)
        self.across_listbox.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.across_listbox.config(yscrollcommand=self.across_scrollbar.set)
        # Across scrollbar
        self.across_scrollbar.config(command=self.across_listbox.yview)
        self.across_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)
        # Down label
        self.down_label.config(text="Down", anchor=tk.W, **clues_style)
        self.down_label.grid(row=2, column=0, pady=(PAD, 0), sticky=tk.N+tk.W)
        # Down frame
        self.down_frame.config(highlightthickness=1, highlightbackground=appearance.clues.fg)
        self.down_frame.grid(row=3, pady=(TINY_PAD, 0), sticky=tk.N+tk.S)
        self.down_frame.rowconfigure(0, weight=1)
        # Down listbox
        self.down_listbox.config(bd=0, selectborderwidth=0, activestyle=tk.NONE, **list_style)
        self.down_listbox.grid(row=0, column=0, sticky=tk.N+tk.S)
        self.down_listbox.config(yscrollcommand=self.down_scrollbar.set)
        # Down scrollbar
        self.down_scrollbar.config(command=self.down_listbox.yview)
        self.down_scrollbar.grid(row=0, column=1, sticky=tk.N+tk.S)


class ChatView(SubView):
    """The chat group of the crossword application."""

    def __init__(self, parent: View, frame: tk.Frame):
        """Build the chat widget group."""
        super().__init__(parent, frame)

    def load(self):
        """Configure the graphical components of the group."""
        pass


class ListVar:
    """Mock tkinter list variable."""

    def __init__(self, listbox):
        """Initialize the list variable with a listbox."""
        self.listbox = listbox

    def set(self, values):
        """Set the contents of the list variable and listbox."""
        self.clear()
        for value in values:
            self.listbox.insert(tk.END, value)

    def get(self):
        """Get the contents of the listbox."""
        return self.listbox.get()

    def clear(self):
        """Clear the listbox."""
        self.listbox.delete(0, tk.END)


class JoinDialog:
    """Crossword server join dialog."""

    def __init__(self, defaults=None):
        """Build the server join dialog."""
        defaults = dict(defaults)
        # Passed members
        self.result = None
        # Root
        self.root = tk.Tk()
        self.root.title("Join Server")
        # Content frame
        self.frame = tk.Frame(self.root)
        # Name entry
        self.name = tk.StringVar()
        self.name.set(defaults.get("name", ""))
        self.name_entry = tk.Entry(self.frame, textvariable=self.name)
        # Color entry
        self.color = tk.StringVar()
        self.color.set(defaults.get("color", COLORS[0]))
        self.color_selector = tk.OptionMenu(self.frame, self.color, *COLORS)
        self.color_selector.config(anchor=tk.W)
        # Address entry
        self.address = tk.StringVar()
        self.address.set(defaults.get("address", "127.0.0.1"))
        self.address_selector = tk.Entry(self.frame, textvariable=self.address)
        # Buttons
        self.quit_button = tk.Button(self.frame, text="Quit", command=self.quit)
        self.connect_button = tk.Button(self.frame, text="Connect", command=self.connect)
        self.load()

    def load(self):
        """Load the server join dialog."""
        self.frame.grid(padx=5, pady=5)
        self.name_entry.config(width=40)
        self.name_entry.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        self.color_selector.grid(row=1, column=0, columnspan=3, padx=3, pady=5, sticky=tk.W+tk.E)
        self.address_selector.grid(row=2, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W+tk.E)
        self.frame.columnconfigure(0, weight=1)
        self.connect_button.grid(row=3, column=2, pady=5, padx=5, sticky=tk.E)
        self.quit_button.grid(row=3, column=1, pady=5, sticky=tk.E)

    def validate(self):
        """Validate the input in the server join dialog."""
        if self.name.get() and self.color.get() and self.address.get():
            self.connect_button.config(state=tk.NORMAL)
        else:
            self.connect_button.config(state=tk.DISABLED)
        self.root.after(50, self.validate)

    def quit(self):
        """Quit the server join dialog."""
        self.root.destroy()

    def connect(self):
        """Finish input to the server join dialog."""
        name = self.name.get()
        color = self.color.get().lower()
        split = self.address.get().split(":")
        address = (split[0], settings.network.server.port if len(split) == 1 else int(split[1]))
        self.result = {"name": name, "color": color, "address": address}
        self.root.destroy()

    def main(self):
        """Run the main loop of the view."""
        self.validate()
        self.root.mainloop()


def join_dialog(defaults=None):
    """Run a server join dialog and return the user's input."""
    jd = JoinDialog(defaults)
    jd.main()
    return jd.result


def puzzle_dialog():
    """Run a puzzle file dialog and return the file path."""
    path = fd.askopenfilename(title="Select a puzzle")
    return path
