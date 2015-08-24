from crossword import network
import time

connection = network.SocketConnection(("127.0.0.1", 50000))
connection.start()
connection.emit("echo", "Hello, world!")
connection.emit("echo", "What?")
time.sleep(5)
connection.stop()
print("stopped")
