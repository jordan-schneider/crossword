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


# Global
settings = None


# JSON
def load(settings_path=SETTINGS_PATH):
    """Load the settings JSON file specified by `settings_path`.

    If the file does not exist or cannot be parsed into JSON the
    function returns None.

    settings_path - the path to the settings file.
    """

    global settings
    try:
        with open(settings_path) as settings_file:
            settings = json.load(settings_file)
    except (FileNotFoundError, ValueError):
        settings = None


def save(settings_path=SETTINGS_PATH):
    """Save the settings JSON object to `settings_path`.

    settings - the settings JSON object.
    settings_path - the path to the settings file.
    """

    global settings
    with open(settings_path, "w") as settings_file:
        json.dump(settings, settings_file, indent=2, sort_keys=True)


# Allow access from outside
def get(option, default=None):
    """Get a settings option using `:` separator syntax.

    Example: "window:line-fill"

    If the setting does not exist the function returns the `default`
    parameter value.
    """

    global settings
    current = settings
    for node in option.split(":"):
        current = current.get(node)
        if current is None:
            return default
    return current


def set(option, value):
    """Set a settings option using `:` separator syntax.

    Example: "window:line-fill"
    """

    global settings
    current = settings
    *parents, child = option.split(":")
    for key in parents:
        current = current.get(key)
        if not isinstance(current, dict):
            raise ValueError("settings key \"%s\" has a non-dict value" % key)
        if current is None:
            current[key] = {}
    current[child] = value


# Load settings
load()
