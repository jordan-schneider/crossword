from crossword import network

server = network.SocketServer(("127.0.0.1", 50000))

try:
    server.start()
except KeyboardInterrupt:
    server.stop()
