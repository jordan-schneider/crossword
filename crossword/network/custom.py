import os
from . import wrapper
from crossword import puz
import crossword.utility.metrics
from crossword.application import model
from crossword.constants import *


class CrosswordHandler(wrapper.SocketHandler):

    def __init__(self, sock, address, server):
        super().__init__(sock, address, server)
        self.model = model.PlayerModel(name="", color="")
        self.model.id = id(self)


class CrosswordServer(wrapper.SocketServer):

    handler = CrosswordHandler

    def __init__(self, address):
        """Initialize the crossword handler."""
        # Initialize and create a puzzle and metrics tracker
        super().__init__(address)
        self.model = None
        self.metrics = None
        # Create a server puzzle directory
        if not os.path.isdir("puzzles"):
            os.makedirs("puzzles")
        # Bind server events
        self.bind(CLIENT_JOINED, self.on_client_joined)
        self.bind(CLIENT_EXITED, self.on_client_exited)
        self.bind(CLIENT_UPDATED, self.on_client_updated)
        self.bind(PUZZLE_PASSED, self.on_puzzle_passed)
        self.bind(PUZZLE_SUBMITTED, self.on_puzzle_submitted)
        logging.info("%s: bound custom events", self)

    def __repr__(self):
        """Represent the crossword server as a string."""
        return "server"

    def on_client_joined(self, data: dict, handler: CrosswordHandler):
        """Called when a client joins the server."""
        # Update the handler data
        handler.model.update(**data)
        logging.info("%s: client named '%s' joined as %s", self, handler.model["name"], handler.model.id)
        # Update the rest of the clients
        self.update_clients()
        handler.emit(SERVER_UPDATED, {ID: handler.model.id})
        self.emit(CLIENT_JOINED, data)
        # Check if there is a model
        if not self.model:
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            handler.emit(PUZZLE_UPDATED, self.model)

    def on_client_exited(self, data: None, handler: CrosswordHandler):
        """Called when a client leaves the server."""
        # Check if the number of handlers is 0
        if len(self.handlers) == 0:
            self.model = None
        # Update the rest of the clients
        self.update_clients()

    # Puzzle submission
    def on_puzzle_passed(self, data: None, handler: CrosswordHandler):
        """Called when the selected user passes submitting a puzzle."""
        # Ask the next handler for a puzzle
        index = (self.handlers.index(handler) + 1) % len(self.handlers)
        self.handlers[index].emit(PUZZLE_REQUESTED, None)

    def on_puzzle_submitted(self, data: bytes, handler: CrosswordHandler):
        """Called when the selected user submits a puzzle."""
        # Write the received puzzle to a file
        path = os.path.join("puzzles", str(hash(data)) + ".puz")
        with open(path, "wb") as file:
            file.write(data)
        # Try to read the puzzle
        try:
            self.model = model.PuzzleModel(puz.read(path))
        except puz.PuzzleFormatError:
            # Accept failure and ask again
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            # Otherwise, record metrics and update the other players
            self.metrics = crossword.utility.metrics.PuzzleMetrics(self.model)
            self.emit(PUZZLE_UPDATED, self.model)

    # User echo methods
    def on_client_updated(self, data: tuple, handler: CrosswordHandler):
        """Called when a client has updated themself."""
        for key in data:
            # Move the player
            if key == POSITION:
                handler.model.x, handler.model.y = data[POSITION]
            # Change the players direction
            elif key == DIRECTION:
                handler.model.direction = data[DIRECTION]
            # Check if the player changed their cell letter
            elif key == LETTER:  # This is not symbolically correct but works fine.
                x, y, letters = data[LETTER]
                self.model.cells[x, y].letters = letters
                self.model.cells[x, y].owner = handler.model.id
            else:
                print("Warning: received invalid key for player update '%s'." % key)
        # Update the rest of the handlers
        others = self.handlers[:]
        others.remove(handler)
        self.emit(CLIENT_UPDATED, (handler.model.id, data), *others)

    # Special case methods
    def update_clients(self):
        """Updates the clients to the current client list."""
        models = [handler.model for handler in self.handlers]
        for handler in self.handlers:
            # Remove the handler to avoid confusion
            copy = models[:]
            copy.remove(handler.model)
            handler.emit(SERVER_UPDATED, {CLIENTS: copy})


class CrosswordConnection(wrapper.SocketConnection):

    def __init__(self, address):
        super().__init__(address)


