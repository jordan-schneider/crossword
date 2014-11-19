# Graphics
# Crossword
# Noah Kim

"""

.------------------------------. 
|------------------------------| 
| .--------------------------. |
| '--------------------------' |
| .-----------------. .------. |
| |                 | |      | |
| |                 | |      | |
| |                 | |      | | 
| |                 | '------' |
| |                 | .------. |
| |                 | |      | |
| |                 | |      | |
| |                 | |      | |
| '-----------------' '------' |
'------------------------------'

"""


# Import
import tkinter
import puz

# Constant
WINDOW_TITLE = "New York Times Crossword Puzzle"
CELL_SIDE = 30

# Crossword
class CrosswordWindow:
    """A crossword game window."""

    def load(self, puzzle):
        """Load a puzzle to the window."""
        self.puzzle = puz.read(puzzle)

    def build(self):
        """Build the graphical interface."""
        self.window = tkinter.Tk()
        self.window.title(WINDOW_TITLE)
        self.window.resizable(False, False)

        self.frame = tkinter.Frame(self.window)
        self.frame.pack(padx=5, pady=5)

        self.title = tkinter.Label(self.frame, bg="red")
        self.title.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="we")

        self.info = tkinter.Label(self.frame, bg="red")
        self.info.grid(row=1, column=0, padx=5, pady=5, sticky="we")

        self.board = tkinter.Canvas(self.frame, bg="red")
        self.board.config(width=CELL_SIDE*self.puzzle.width + 1,
                           height=CELL_SIDE*self.puzzle.height + 1)
        self.board.grid(row=2, column=0, rowspan=2, padx=2, pady=2)

        self.hints = tkinter.Frame(self.frame)
        self.hints.grid(row=1, column=1, rowspan=3, sticky="ns")

        self.across = tkinter.Listbox(self.hints, bg="red")
        self.across.config(width=35)
        self.across.grid(row=0, column=0, sticky="ns", padx=5, pady=5)

        self.down = tkinter.Listbox(self.hints, bg="red")
        self.down.config(width=35)
        self.down.grid(row=1, column=0, sticky="ns", padx=5, pady=5)

    def run(self):
        self.window.mainloop()
        

cp = CrosswordWindow()
cp.load("puzzles/Nov0705.puz")
cp.build()
cp.run()
