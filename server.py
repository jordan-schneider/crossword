import crossword.network.custom

server = crossword.network.custom.CrosswordServer(("127.0.0.1", 50000))

try:
    server.start()
except KeyboardInterrupt:
    server.stop()
