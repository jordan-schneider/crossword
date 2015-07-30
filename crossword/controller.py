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
        self.reload()

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

    def reload(self):
        self.view.title.set(self.parent.model.title)
        self.view.author.set(self.parent.model.author)


class PuzzleController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.puzzle

    def reload(self):
        for cell in self.model.cells:
            view = self.view.cells[cell.x, cell.y]
            if cell.kind is EMPTY:
                view.update(fill=settings.get("board:fill:empty"))
            elif cell.kind is LETTER:
                view.update(fill=settings.get("board:fill:default"))
                view.update(number=cell.number)
                view.update(letters=cell.solution)


class CluesController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.clues

    def reload(self):
        self.view.across.set(list(map(lambda word: word.clue, self.parent.model.words.across)))
        self.view.down.set(list(map(lambda word: word.clue, self.parent.model.words.down)))
