class Access:

    _cache = []
    _start = []

    def __init__(self, start=None):
        if start and type(start) == list:
            self._start = start
        elif start and type(start) == str:
            self._start = [start]
        self._cache = self._start[:]

    def __getattribute__(self, key):
        if key.startswith("_"):
            return super().__getattribute__(key)
        self._cache.append(key)
        return self

    def __iter__(self):
        copy = self._cache[:]
        self._cache = self._start[:]
        return iter(copy)

    def __str__(self):
        copy = self._cache[:]
        self._cache = self._start[:]
        return ".".join(copy)

    def __repr__(self):
        return ".".join(self)
