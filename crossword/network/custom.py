import os
from . import wrapper
from crossword import puz
import crossword.utility.metrics
from crossword.application import model
from crossword.constants import *


class CrosswordHandler(wrapper.SocketHandler):

    def __init__(self, sock, address, server):
        super().__init__(sock, address, server)
        self.model = model.PlayerModel("", "")
        self.model.id = self.address[0]


class CrosswordServer(wrapper.SocketServer):

    handler = CrosswordHandler

    def __init__(self, address):
        super().__init__(address)
        self.model = None
        self.metrics = None

        if not os.path.isdir("puzzles"):
            os.makedirs("puzzles")

        self.bind(CLIENT_JOINED, self.on_client_joined)
        self.bind(CLIENT_EXITED, self.on_client_exited)
        self.bind(PUZZLE_PASSED, self.on_puzzle_passed)
        self.bind(PUZZLE_SUBMITTED, self.on_puzzle_submitted)
        self.bind(CLIENT_UPDATED, self.on_client_updated)
        logging.info("%s: bound custom events", self)

    def __repr__(self):
        return "server"

    def on_client_joined(self, data: dict, handler: CrosswordHandler):
        handler.model.name = data["name"]
        handler.model.color = data["color"]
        print("client named '%s' joined as %s" % (handler.model.name, handler.model.id))

        self.update_clients()
        self.emit(CLIENT_JOINED, data)

        if not self.model:
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            handler.emit(PUZZLE_UPDATED, self.model)

    def on_client_exited(self, data: dict, handler: CrosswordHandler):
        if len(self.handlers) == 0:
            self.model = None

    # Puzzle submission
    def on_puzzle_passed(self, data: None, handler: CrosswordHandler):
        index = (self.handlers.index(handler) + 1) % len(self.handlers)
        self.handlers[index].emit(PUZZLE_REQUESTED, None)

    def on_puzzle_submitted(self, data: bytes, handler: CrosswordHandler):
        path = os.path.join("puzzles", str(hash(data)) + ".puz")
        with open(path, "wb") as file:
            file.write(data)

        try:
            self.model = model.PuzzleModel(puz.read(path))
        except:
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            self.metrics = crossword.utility.metrics.PuzzleMetrics(self.model)
            self.emit(PUZZLE_UPDATED, self.model)

    # User echo methods
    def on_client_updated(self, data: tuple, handler: CrosswordHandler):
        for key in data:
            if key == POSITION:
                handler.model.x, handler.model.y = data[POSITION]
            elif key == DIRECTION:
                handler.model.direction = data[DIRECTION]
            elif key == LETTER:  # This is not symbolically correct but works fine.
                x, y, letters = data[LETTER]
                self.model.cells[x, y].letters = letters
                self.model.cells[x, y].owner = handler.model.id
            else:
                print("Warning: received invalid key for player update '%s'." % key)
        others = self.handlers[:]
        others.remove(handler)
        self.emit(CLIENT_UPDATED, (handler.model.id, data), *others)

    # Special case methods
    def update_clients(self):
        models = [handler.model for handler in self.handlers]
        for handler in self.handlers:
            copy = models[:]
            copy.remove(handler.model)
            self.emit(SERVER_UPDATED, {CLIENTS: copy})


class CrosswordConnection(wrapper.SocketConnection):

    def __init__(self, address):
        super().__init__(address)


