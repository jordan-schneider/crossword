# Crossword
# Noah Kim

# Logging
import logging
from logging import FATAL, CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
logging.basicConfig(format="%(levername)8s %(asctime)s %(message)s", datefmt="%I:%M:%S %p", level=NOTSET)
logging.log(INFO, "logging started")

# Import
import tkinter
import threading
import queue
import socket
import struct
import pickle
import string
import time
import datetime
import platform
import sys

import puz

# Constant
LETTER = "-"
EMPTY = "."
DOWN = "down"
ACROSS = "across"

WINDOWS_FONT_MODIFIER = -5
DARWIN_FONT_MODIFIER = 0
ACTIVE_FONT_MODIFIER = DARWIN_FONT_MODIFIER if platform.system() == "Darwin" else WINDOWS_FONT_MODIFIER

# Configuration
def get_any_value(string):
    """Determine any possible value in a string. This is a cheap method that is only implemented as convenience for the
    namespace config file reader."""
    try: return eval(string, {}, {})
    except: return string

class Config:
    """This is a mutable configuration namespace. It contains all configurable and builtin options for the crossword app
    and its related network components. It also has the ability to read and write from a configuration file, but this
    should only be used on initialization, changes by the user in the setting menu, and deletion."""

    class graphics:
        """Graphics portion of the configuration namespace."""
        cell_size = 33
        font_family = "tkDefaultFont"
        font_size_modifier = 0
        font_color = "black"
        fill_deselected = "white"
        fill_selected_word = "light blue"
        fill_selected_letter = "yellow"


    class behavior: ...