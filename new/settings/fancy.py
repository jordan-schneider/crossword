database = {}


class Access:

    def __init__(self):
        self._cache = []
        database[id(self)] = self._cache

    def __setattr__(self, key, value):
        if key == "_cache":
            raise KeyError("Cannot overwrite  `_cache` of Access")
        self._cache.append(key)
        super().__setattr__(key, value)

    def __getattribute__(self, key):
        try:
            return super().__getattribute__(key)
        except AttributeError:
            access = Access()
            self.__setattr__(key, access)
            self._cache.append(key)
        return access

    def __repr__(self):
        return "{" + ", ".join(self._cache) + "}"

