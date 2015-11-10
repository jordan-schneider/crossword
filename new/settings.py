# Import
import xml.etree.ElementTree
import os
from . import resource
from .constants import *

# Read the resource
copy = resource.read(os.path.join(COPY, SETTINGS))
resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS)
