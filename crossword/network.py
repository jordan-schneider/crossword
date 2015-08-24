import socket
import struct
import queue
import threading
import pickle
from .constants import *

# Socket utility
def send(sock: socket.socket, message: bytes):
    """Pack the message length and content for sending larger messages."""
    print("send size", len(message))
    message = struct.pack('>I', len(message)) + message
    sock.sendall(message)


def recv(sock: socket.socket):
    """Read message length and receive the corresponding amount of data."""
    size = _recv(sock, 4)
    size = struct.unpack('>I', size)[0]
    print("recv size", size)
    return _recv(sock, size)


def _recv(sock: socket.socket, size: int):
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
class SocketServer:

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
                handler = SocketHandler(sock, address, self)
                handler.start()
                self.handlers.append(handler)
            except Exception as e:
                print("server accept", e)
                self.stop()

    def serve(self):
        while self.alive:
            try:
                event, data = self.queue.get()
                function = self.bindings.get(event)
                if function is None:
                    print("caught event %s with no binding" % event)
                function(data)
            except Exception as e:
                print("server serve", e)
                self.stop()

    def emit(self, event, data, *handlers):
        handlers = handlers or self.handlers
        for handler in handlers:
            handler.emit(event, data)

    def bind(self, event, function):
        self.bindings[event] = function

    def echo(self, data):
        print(data)
        self.emit("echo", data)

    def start(self):
        self.alive = True
        self._accept.start()
        self.serve()

    def stop(self):
        self.alive = False
        for handler in self.handlers:
            handler.stop()


class SocketHandler:

    def __init__(self, sock, address, server):
        self.sock = sock
        self.address = address
        self.server = server
        self.alive = False

        self._receive = threading.Thread(target=self.receive, daemon=True)

    def receive(self):
        while self.alive:
            try:
                raw = recv(self.sock)
                event, data = pickle.loads(raw)
                self.server.queue.put((event, data))
            except Exception as e:
                print("handler receive", e)
                self.stop()

    def emit(self, event, data):
        send(self.sock, pickle.dumps((event, data)))

    def start(self):
        self.alive = True
        self._receive.start()

    def stop(self):
        self.alive = False
        if self in self.server.handlers:
            self.server.handlers.remove(self)


class SocketConnection:

    def __init__(self, address):
        self.address = address
        self.alive = False

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.address)

        self._receive = threading.Thread(target=self.receive, daemon=True)

    def receive(self):
        while self.alive:
            try:
                event, data = pickle.loads(recv(self.sock))
                print(data)
            except Exception as e:
                print("connection receive", e)
                self.stop()

    def emit(self, event, data):
        send(self.sock, pickle.dumps((event, data)))

    def start(self):
        self.alive = True
        self._receive.start()

    def stop(self):
        self.alive = False


class CrosswordServer(SocketServer):
    pass


class CrosswordHandler(SocketHandler):
    pass


class CrosswordConnection(SocketConnection):
    pass


