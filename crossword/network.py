import socket
import struct
import queue
import threading
import pickle


# Socket utility
def send(sock: socket.socket, message: bytes):
    """Pack the message length and content for sending larger messages."""
    message = struct.pack('>I', len(message)) + message
    sock.sendall(message)


def recv(sock: socket.socket):
    """Read message length and receive the corresponding amount of data."""
    size = _recv(sock, 4)
    if not size:
        return None
    size = struct.unpack('>I', size)[0]
    return _recv(sock, size)


def _recv(sock: socket.socket, size: int):
    """Secondary function to receive a specified amount of data."""
    message = b''
    while len(message) < size:
        packet = sock.recv(size - len(message))
        if not packet:
            return None
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

        self._accept = threading.Thread(target=self.accept)

    def accept(self):
        while self.alive:
            try:
                sock, address = self.sock.accept()
                sock.setblocking(False)
                handler = SocketHandler(sock, address, self)
                handler.start()
                self.handlers.append(handler)
            except Exception as e:
                print(e)
                self.stop()

    def serve(self):
        while self.alive:
            try:
                hook, data = self.queue.get()
                function = self.bindings.get(hook)
                if function is None:
                    print("caught hook %s with no binding" % hook)
                function(data)
            except Exception as e:
                print(e)
                self.stop()

    def emit(self, hook, data, *handlers):
        handlers = handlers or self.handlers
        for handler in handlers:
            handler.emit(hook, data)

    def bind(self, hook, function):
        self.bindings[hook] = function

    def echo(self, data):
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

        self._receive = threading.Thread(target=self.receive)

    def receive(self):
        while self.alive:
            try:
                hook, data = pickle.loads(recv(self.sock))
                self.server.queue.put((hook, data))
            except WindowsError:
                pass
            except Exception as e:
                print(e)
                self.stop()

    def emit(self, hook, data):
        send(self.sock, pickle.dumps((hook, data)))

    def start(self):
        self.alive = True
        self._receive.start()

    def stop(self):
        self.alive = False
        self.server.handlers.remove(self)
        print("removed handler")


class SocketConnection:

    def __init__(self, address):
        self.address = address
        self.alive = False

        self.sock = socket.socket()
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect(self.address)

        self._receive = threading.Thread(target=self.receive)

    def receive(self):
        while self.alive:
            try:
                hook, data = pickle.loads(recv(self.sock))
                print(hook, data)
            except Exception as e:
                print(e)
                self.stop()

    def emit(self, hook, data):
        send(self.sock, pickle.dumps((hook, data)))

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


