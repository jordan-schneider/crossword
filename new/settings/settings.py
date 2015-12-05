# Import
import xml.etree.ElementTree
import os

from . import cast
from new import utility
from new import system
from new.constants import *


# Read the resource
copy = system.resource.read(os.path.join(COPY, SETTINGS))
system.resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS).getroot()

settings = utility.fancy.Access("settings")


def _get(path, parent):
    if not path:
        return parent
    for child in parent.getchildren():
        if child.get("name") == path[0]:
            path.pop(0)
            return _get(path, child)
    return None


def get(access: utility.fancy.Access):
    path = list(access)[1:]  # Ignore settings prefix
    node = _get(path, tree)
    if node is None:
        return None
    return cast.cast(node)


