# Import
import xml.etree.ElementTree
import os

from . import translate
from new import utility
from new import system
from new.constants import *


# Read the resource
copy = system.resource.read(os.path.join(COPY, SETTINGS))
system.resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS).getroot()


def _settings(path, parent):
    if not path:
        return parent
    for child in parent.getchildren():
        if child.get("name") == path[0]:
            path.pop(0)
            return _settings(path, child)
    return None

crossword = utility.fancy.Access("crossword")


class Settings:

    def __getitem__(self, access: utility.fancy.Access):
        path = list(access)[1:]  # Ignore settings prefix
        node = _settings(path, tree)
        if node is None:
            return None
        return translate.cast(node)

settings = Settings()




