# Import
import xml.etree.ElementTree
import collections
import os

from . import translate
from crossword import utility
from crossword import system
from crossword.constants import *


# Read the resource
copy = system.resource.read(os.path.join(COPY, SETTINGS))
system.resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS).getroot()


# Define some useful containers
class Node:

    __dir = []

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if not key.startswith("_"):
            self.__dir.append(key)

    def __iter__(self):
        return iter(getattr(self, name) for name in self.__dir)


class Settings(Node):

    __src = None
    __map = {}

    def __init__(self, source: xml.etree.ElementTree.ElementTree):
        self.__src = source

    def __getitem__(self, item):
        if isinstance(item, collections.Iterable):
            item = ".".join(item)
        elif type(item) == utility.fancy.Access:
            item = str(item)
        return self.__map[item]

    def __setitem__(self, key, value):
        self.__map[key] = value


settings = Settings(tree)


def load():
    _load(tree, "", settings)


def _load(node, path, cursor):
    for child in node:
        name = child.get("name")
        path = name if not path else ".".join([path, name])
        if child.tag == "option":
            value = translate.cast(child)
            setattr(cursor, name, value)
            settings[path] = value
        else:
            descendant = type(child.tag, (Node,), {})
            setattr(cursor, name, descendant)
            _load(child, path, descendant)


load()
