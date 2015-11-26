class Access:

    def __init__(self):
        self._cache = []

    def __getattribute__(self, key):
        if key.startswith("_"):
            return super().__getattribute__(key)
        self._cache.append(key)
        return self

    def __repr__(self):
        qualified = ".".join(self._cache)
        self._cache = []
        return qualified
