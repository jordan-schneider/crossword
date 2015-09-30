import socket
import struct
import queue
import threading
import pickle
from . import puz
from . import model as _model
from . import metrics as _metrics
from .constants import *


# Socket utility
def send(sock: socket.socket, message: bytes):
    """Pack the message length and content for sending larger messages."""
    message = struct.pack('>I', len(message)) + message
    sock.sendall(message)


def recv(sock: socket.socket) -> bytes:
    """Read message length and receive the corresponding amount of data."""
    size = _recv(sock, 4)
    size = struct.unpack('>I', size)[0]
    return _recv(sock, size)


def _recv(sock: socket.socket, size: int) -> bytes:
    """Secondary function to receive a specified amount of data."""
    message = b''
    while len(message) < size:
        packet = sock.recv(size - len(message))
        if not packet:
            sock.close()
            raise OSError("Nothing else to read from socket")
        message += packet
    return message


# Socket wrapper classes
class SocketHandler:
    """Socket server worker base class.
    
    The socket handler deals with sending and receiving messages from
    the connected client.
    """

    def __init__(self, sock: socket.socket, address: str, server):
        """Initialize a new socket handler."""
        self.sock = sock
        self.address = address
        self.server = server
        self.alive = False

        self._receive = threading.Thread(target=self.receive, daemon=True)

    def receive(self):
        """Receive loop that queues incoming messages."""
        while self.alive:
            try:
                event, data = pickle.loads(recv(self.sock))
                self.server.queue.put((event, data, self))
            except Exception as e:
                print("handler receive", e)
                self.server.queue.put((CLIENT_EXITED, None, self))
                self.stop()

    def emit(self, event: str, data: object):
        """Send a message to the connected client."""
        send(self.sock, pickle.dumps((event, data)))

    def start(self):
        """Start the socket handler."""
        self.alive = True
        self._receive.start()

    def stop(self):
        """Stop the socket handler."""
        self.alive = False
        if self in self.server.handlers:
            self.server.handlers.remove(self)
        self.server.emit(CLIENT_EXITED, "")


class SocketServer:

    handler = SocketHandler

    def __init__(self, address):
        self.address = address
        self.alive = False

        self.queue = queue.Queue()
        self.handlers = []
        self.bindings = {}

        self.sock = socket.socket()
        self.sock.bind(self.address)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.listen(8)

        self.bind("echo", self.echo)

        self._accept = threading.Thread(target=self.accept, daemon=True)

    def accept(self):
        while self.alive:
            try:
                sock, address = self.sock.accept()
                handler = self.handler(sock, address, self)
                handler.start()
                self.handlers.append(handler)
            except Exception as e:
                print("server accept", e)
                self.stop()

    def receive(self):
        while self.alive:
            event, data, handler = self.queue.get()
            function = self.bindings.get(event)
            if function is None:
                print("caught event %s with no binding" % event)
            else:
                function(data, handler)

    def emit(self, event: str, data: object, *handlers: SocketHandler):
        handlers = handlers or self.handlers
        for handler in handlers:
            handler.emit(event, data)

    def bind(self, event, function):
        self.bindings[event] = function

    def echo(self, data, handler):
        handler.emit(data)

    def start(self):
        self.alive = True
        self._accept.start()
        self.receive()

    def stop(self):
        self.alive = False
        for handler in self.handlers:
            handler.stop()


class SocketConnection:

    def __init__(self, address):
        self.address = address
        self.alive = False

        self.q = queue.Queue()

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.address)

        self._receive = threading.Thread(target=self.receive, daemon=True)

    def receive(self):
        while self.alive:
            try:
                event, data = pickle.loads(recv(self.sock))
                self.q.put((event, data))
            except Exception as e:
                print("connection receive", e)
                self.stop()

    def emit(self, event: str, data: object):
        send(self.sock, pickle.dumps((event, data)))

    def queue(self, q: queue.Queue):
        self.q = q

    def start(self):
        self.alive = True
        self._receive.start()

    def stop(self):
        self.alive = False


class CrosswordHandler(SocketHandler):

    def __init__(self, sock, address, server):
        super().__init__(sock, address, server)
        self.model = _model.PlayerModel("", "")
        self.model.id = self.address[0]


class CrosswordServer(SocketServer):

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
        self.bind(CELL_SELECTED, self.on_cell_selected)
        self.bind(DIRECTION_SET, self.on_direction_set)
        self.bind(LETTER_INSERTED, self.on_letter_inserted)

    def on_client_joined(self, data: dict, handler: CrosswordHandler):
        handler.model.name = data["name"]
        handler.model.color = data["color"]
        print("client named '%s' joined as %s" % (handler.model.name, handler.model.id))

        self.broadcast_client_list()

        if not self.model:
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            handler.emit(PUZZLE_UPDATE, self.model)

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
            self.model = _model.PuzzleModel(puz.read(path))
        except:
            handler.emit(PUZZLE_REQUESTED, None)
        else:
            self.metrics = _metrics.PuzzleMetrics(self.model)
            self.emit(PUZZLE_SUBMITTED, data)

    # User echo methods
    def on_cell_selected(self, data: tuple, handler: CrosswordHandler):
        handler.model.x, handler.model.y = data
        self.emit(CELL_SELECTED, (handler.model.id, data))

    def on_direction_set(self, data: str, handler: CrosswordHandler):
        handler.model.direction = data
        self.emit(DIRECTION_SET, (handler.model.id, data))

    def on_letter_inserted(self, data: tuple, handler: CrosswordHandler):
        x, y, letters = data
        self.model.cells[x, y].letters = letters
        self.model.cells[x, y].owner = handler.model.id
        others = self.handlers[:]
        others.remove(handler)
        self.emit(LETTER_INSERTED, (handler.model.id, data), *others)

    # Special case methods
    def broadcast_client_list(self):
        models = [handler.model for handler in self.handlers]
        for handler in self.handlers:
            copy = models[:]
            copy.insert(0, copy.pop(copy.index(handler.model)))
            self.emit(CLIENT_LIST_UPDATED, copy)


class CrosswordConnection(SocketConnection):

    def __init__(self, address):
        super().__init__(address)


