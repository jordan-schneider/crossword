from crossword import controller

from sys import argv

args = argv[1:]

if len(argv) not in [1, 4]:
    print("Incorrect number of arguments. Usage:\n%s username colour host:port\nor: %s (to use defaults)" % (argv[0],
                                                                                                             argv[1]))
    exit(1)


if len(argv) == 1:
    args = ["Noah", "black", "127.0.0.1:50000"]

host = []
try:
    host = args[2].split(":")
    if len(host) != 2:
        print("Host format: host:port")
        exit(1)
    host[1] = int(host[1])
except ValueError:
    print("Port must be an integer")
    exit(1)

args[2] = tuple(host)

application = controller.Controller(*args)
application.main()
print("stopped")
