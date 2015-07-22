"""Crossword Application Constants.

Settings handles persistent user configurations, which are stored as
JSON files in the local directory.
"""


# Data
__author__ = "Noah Kim"
__version__ = "0.2.0"
__status__ = "Development"


# Import
import json
from .constants import *


# JSON
def load(settings_path=SETTINGS_PATH):
    try:
        with open(settings_path) as settings_file:
            return json.load(settings_file)
    except (FileNotFoundError, ValueError):
        return None


# Calculated
CELL_SIZE = 33