from .constants import *


class Connection:

    def __init__(self, address, mode=CLIENT):
        self.address = address
        self.mode = mode

    def emit(self):
        pass

    def bind(self, event, hook):
        pass

    def main(self):
        pass

    def stop(self):
        pass

