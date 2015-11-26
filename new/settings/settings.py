# Import
import xml.etree.ElementTree
import os

from new.system import resource
from . import fancy
from new.constants import *

# Read the resource
copy = resource.read(os.path.join(COPY, SETTINGS))
resource.ease(SETTINGS, copy=copy).close()
tree = xml.etree.ElementTree.parse(SETTINGS).getroot()

settings = fancy.Access()

def get(option):
    sections = str(option).split(".")
