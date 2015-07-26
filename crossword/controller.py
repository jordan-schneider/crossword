from . import view
from . import model


class Controller:

    def __init__(self):
        self.view = view.View()
        self.model = None
        self.selection = model.SelectionModel()


    def load_puzzle(self, model: model.PuzzleModel):
        self.model = model
        self.view.header.title = self.model.title
        self.view.header.author = self.model.author

    def draw_puzzle(self):
        pass

    def draw_word(self, word: model.WordModel):
        pass

    def draw_cell(self, cell: model.CellModel):
        pass

class CrosswordController: pass


class CluesController: pass


class PuzzleController: pass


class ChatController: pass


