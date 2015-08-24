from crossword import network

connection = network.SocketConnection(("127.0.0.1", 50000))
connection.emit("echo", {"message": "hello"})
