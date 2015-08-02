import tkinter as tk
import string
from . import view as _view
from . import model as _model
from . import settings
from .constants import *


class Controller:

    def __init__(self):
        self.view = _view.View()
        self.model = None
        self.player = _model.PlayerModel("Test", "Black")
        self.header = HeaderController(self)
        self.puzzle = PuzzleController(self)
        self.clues = CluesController(self)

    def reload(self):
        self.header.reload()
        self.puzzle.reload()
        self.clues.reload()

    def load(self, model: _model.PuzzleModel):
        self.model = model
        self.header.load()
        self.puzzle.load()
        self.clues.load()

    def main(self):
        self.view.main()


class SubController:

    def __init__(self, parent: Controller):
        self.parent = parent

    @property  # This is a property because the model is not permanent
    def model(self):
        return self.parent.model

    @property  # This is a property because I'm unsure of how it will work
    def player(self):
        return self.parent.player

    def reload(self):
        pass


class HeaderController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.header

    def load(self):
        self.view.title.set(self.parent.model.title)
        self.view.author.set(self.parent.model.author)

    reload = load


class PuzzleController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.puzzle
        # Reference
        self.current = None
        # Bindings
        self.view.canvas.bind("<Button-1>", self.on_left_click)
        self.view.canvas.bind("<Key>", self.on_key)

    def load(self):
        d = settings.get("board:fill:default")
        e = settings.get("board:fill:empty")
        for cell in self.model.cells:
            cell.fill = d if cell.kind == LETTER else e
            self.draw(cell)

    def draw(self, model: (_model.CellModel, _model.WordModel)):
        if isinstance(model, _model.CellModel):
            self.view.canvas.delete(*list(model.drawings))
            x, y = model.x, model.y
            s = settings.get("board:cell-size")
            bbox = (x*s, y*s, (x+1)*s, (y+1)*s)
            model.drawings.box = self.view.canvas.create_rectangle(*bbox, fill=model.fill)
            if model.letters:
                h = s // 2 + 1
                pos = (x*s + h, y*s + h)
                letters = model.letters
                font = (settings.get("board:font-family"), int(s / (1.1 + 0.6*len(model.letters)))-3)
                color = model.color
                model.drawings.letters = self.view.canvas.create_text(*pos, text=letters, font=font, fill=color)
            if model.number:
                pos = (x*s + NUMBER_LEFT, y*s + NUMBER_TOP)
                number = model.number
                font = (settings.get("board:font-family"), int(s / 3.5)-2)
                model.drawings.number = self.view.canvas.create_text(*pos, text=number, font=font, anchor=tk.W)
        elif isinstance(model, _model.WordModel):
            for cell in model.cells:
                self.draw(cell)

    def on_left_click(self, event):
        # Get focus
        self.view.canvas.focus_set()
        # Efficiently access instance members
        s = settings.get("board:cell-size")
        x = (event.x - CANVAS_PAD - 1) // s
        y = (event.y - CANVAS_PAD - 1) // s
        cell = self.model.cells[x, y]
        # Ignore if the cell is empty
        if cell.kind == EMPTY:
            return
        # Change direction if the clicked cell is selected
        if cell == self.current:
            self.player.direction = [ACROSS, DOWN][self.player.direction == ACROSS]
        # Select the cell
        self.select_cell(cell)

    def on_key(self, event):
        # If the key is a backspace
        if event.keysym == "BackSpace":
            self.remove_letter()
        # If the key is a letter
        if event.keysym in string.ascii_letters:
            self.insert_letter(event.keysym)

    def select_cell(self, cell: _model.CellModel):
        # Ignore if the cell is empty
        if cell.kind == EMPTY:
            raise TypeError("Cannot select an empty cell")
        # If there is a selection, clear it
        if self.current:
            word = self.current.word[self.player.direction]
            word.fill = settings.get("board:fill:default")
            self.draw(word)
        # Change the fill of the word and selected cell
        cell.word[self.player.direction].fill = settings.get("board:fill:selected")
        cell.fill = settings.get("board:fill:selected-letter")
        # Draw the word
        self.draw(cell.word[self.player.direction])
        # Set the current selection
        self.current = cell

    def move_current(self, distance=1, absolute=True):
        pass

    def next_word(self, count=1):
        pass

    def insert_letter(self, letter: str):
        # If there is a current cell
        if self.current:
            self.current.owner = self.player
            if letter in string.ascii_lowercase:
                self.current.letters = letter.upper()
            elif letter in string.ascii_uppercase:
                self.current.letters += letter.upper()
            self.draw(self.current)

    def remove_letter(self):
        # If there is a current cell
        if self.current:
            self.current.letters = self.current.letters[:-1]
            self.draw(self.current)

class CluesController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.clues

    def load(self):
        self.view.across.set(list(map(lambda word: word.clue, self.parent.model.words.across)))
        self.view.down.set(list(map(lambda word: word.clue, self.parent.model.words.down)))

    reload = load
