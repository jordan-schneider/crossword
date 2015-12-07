import socket
import struct
import queue
import threading
import pickle
from crossword.constants import *


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
    """Socket server worker default class.

    The socket handler deals with sending and receiving messages from
    the connected client.
    """

    def __init__(self, sock: socket.socket, address: str, server):
        """Initialize a crossword socket handler."""
        self.sock = sock
        self.address = address
        self.server = server
        self.alive = False

        self._receive = threading.Thread(target=self.receive, daemon=True)
        logging.info("%s: finished initialization", self)

    def __repr__(self):
        return "SocketHandler"

    def receive(self):
        """Receive loop that queues incoming messages."""
        while self.alive:
            try:
                event, data = pickle.loads(recv(self.sock))
                self.server.queue.put((event, data, self))
            except Exception as e:
                logging.error("%s receive caught '%s'", self, e)
                self.server.queue.put((CLIENT_EXITED, None, self))
                self.stop()

    def emit(self, event: str, data: object):
        """Send a message to the connected client."""
        send(self.sock, pickle.dumps((event, data)))

    def start(self):
        """Start the socket handler."""
        self.alive = True
        self._receive.start()
        logging.info("%s: started receive loop", self)

    def stop(self):
        """Stop the socket handler."""
        self.alive = False
        if self in self.server.handlers:
            self.server.handlers.remove(self)
        self.server.emit(CLIENT_EXITED, "")
        logging.info("%s: all processes stopped", self)


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
        logging.info("%s: initialized and bound socket", self)

    def __repr__(self):
        return "SocketServer"

    def accept(self):
        while self.alive:
            try:
                sock, address = self.sock.accept()
                handler = self.handler(sock, address, self)
                handler.start()
                self.handlers.append(handler)
            except Exception as e:
                logging.error("%s: accept caught '%s'", self, e)
                self.stop()

    def receive(self):
        while self.alive:
            event, data, handler = self.queue.get()
            function = self.bindings.get(event)
            if function is None:
                logging.warning("%s: caught event '%s' with no binding", self, event)
            else:
                function(data, handler)

    def emit(self, event: str, data: object, *handlers: SocketHandler):
        handlers = handlers or self.handlers
        for handler in handlers:
            handler.emit(event, data)

    def bind(self, event, function):
        self.bindings[event] = function

    def echo(self, data, handler):
        handler.emit("echoed from " + self.address[0] + ": " + data)

    def start(self):
        self.alive = True
        self._accept.start()
        logging.info("%s: started server loop", self)
        self.receive()

    def stop(self):
        self.alive = False
        for handler in self.handlers:
            handler.stop()
        logging.info("%s: stopped all processes", self)


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
