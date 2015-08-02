import tkinter as tk
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
        self.view.canvas.bind(BUTTON_1, self.on_left_click)

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
        self.view.canvas.focus_set()
        if self.current:
            word = self.current.word[self.player.direction]
            word.fill = settings.get("board:fill:default")
            self.draw(word)
        s = settings.get("board:cell-size")
        x = (event.x - CANVAS_PAD - 1) // s
        y = (event.y - CANVAS_PAD - 1) // s
        cell = self.model.cells[x, y]
        if cell == self.current:
            self.player.direction = [ACROSS, DOWN][self.player.direction == ACROSS]
        if cell.kind == EMPTY:
            return
        cell.word[self.player.direction].fill = settings.get("board:fill:selected")
        cell.fill = settings.get("board:fill:selected-letter")
        self.draw(cell.word[self.player.direction])
        self.current = cell


class CluesController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.clues

    def load(self):
        self.view.across.set(list(map(lambda word: word.clue, self.parent.model.words.across)))
        self.view.down.set(list(map(lambda word: word.clue, self.parent.model.words.down)))

    reload = load
