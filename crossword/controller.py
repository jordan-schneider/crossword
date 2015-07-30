from . import view as _view
from . import model as _model


class Controller:

    def __init__(self):
        self.view = _view.View()
        self.model = None
        self.crossword = CrosswordController(self)

    def load_puzzle(self, model: _model.PuzzleModel):
        self.model = model
        self.view.header.title = self.model.title
        self.view.header.author = self.model.author

    def main(self):
        self.view.main()


class SubController:

    def __init__(self, parent: Controller):
        self.parent = parent


class CrosswordController(SubController):

    def __init__(self, parent: Controller):
        super().__init__(parent)


class CluesController: pass


class PuzzleController: pass


class ChatController: pass


