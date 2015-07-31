from . import view as _view
from . import model as _model
from . import settings
from .constants import *


class Controller:

    def __init__(self):
        self.view = _view.View()
        self.model = None
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
        self.reload()

    def reload(self, individual=None):
        if isinstance(individual, _model.WordModel):
            cells = individual.cells
        elif isinstance(individual, _model.CellModel):
            cells = [individual]
        elif individual is None:
            cells = self.model.cells
        else:
            raise TypeError("Can only reload a cell or word, not %s" % repr(individual))
        for cell in cells:
            view = self.view.cells[cell.x, cell.y]
            view.update(color=cell.color, fill=cell.fill, letters=cell.letters, number=cell.number)

    def on_left_click(self, event):
        self.view.canvas.focus_set()
        if self.current:
            self.current.across.fill = settings.get("board:fill:default")
            self.reload(self.current.across)
        s = settings.get("board:cell-size")
        x = (event.x - CANVAS_PAD - 1) // s
        y = (event.y - CANVAS_PAD - 1) // s
        cell = self.model.cells[x, y]
        if cell.kind == EMPTY:
            return
        cell.across.fill = settings.get("board:fill:selected")
        cell.fill = settings.get("board:fill:selected-letter")
        self.reload(cell.across)
        self.current = cell


class CluesController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.clues

    def load(self):
        self.view.across.set(list(map(lambda word: word.clue, self.parent.model.words.across)))
        self.view.down.set(list(map(lambda word: word.clue, self.parent.model.words.down)))

    reload = load
