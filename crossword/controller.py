from . import view as _view
from . import model as _model


class Controller:

    def __init__(self):
        self.view = _view.View()
        self.model = None
        self.crossword = HeaderController(self)
        self.puzzle = PuzzleController(self)
        self.clues = CluesController(self)

    def reload(self):
        self.crossword.reload()
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
        for y, row in enumerate(self.parent.model.cells):
            for x in enumerate(row):
                pass

class CluesController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)
        self.view = self.parent.view.clues

    def reload(self):
        self.view.set(list(map(lambda word: word.clue, self.parent.model.words.across)))
        self.view.set(list(map(lambda word: word.clue, self.parent.model.words.down)))
