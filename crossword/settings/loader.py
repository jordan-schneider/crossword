# Import
import xml.etree.ElementTree
import os

from crossword import system
from crossword.settings import translate
from crossword.constants import *


# Read the resource
copy = system.resource.read(os.path.join(COPY, SETTINGS))
system.resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS).getroot()


# Define some useful containers
class Node:

    def __init__(self):
        self.__dir = []
        self.__dir.clear()

    def __setattr__(self, key, value):
        super().__setattr__(key, value)
        if not key.startswith("_"):
            self.__dir.append(key)

    def __getitem__(self, item):
        return getattr(self, item)

    def __iter__(self):
        base = [(name, getattr(self, name)) for name in self.__dir]
        return iter(filter(lambda item: not isinstance(item[1], Node), base))


Page = type("Page", (Node,), {})
Section = type("Section", (Node,), {})
Option = type("Option", (Node,), {})
tag = {"page": Page, "section": Section, "option": Option}

settings = Node()


def load():
    _load(tree, "", settings)


def _load(node, path, cursor):
    for child in node:
        name = child.get("name")
        path = name if not path else ".".join([path, name])
        if child.tag == "option":
            value = translate.cast(child)
            setattr(cursor, name, value)
        else:
            descendant = tag[child.tag]()
            setattr(cursor, name, descendant)
            _load(child, path, descendant)
