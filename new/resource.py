"""A collection of various file system tools."""

# Import
import os
from .constants import *


# Main functions
def absolute(local: str):
    """Get the absolute path of a local file or directory."""
    return os.path.join(ROOT, local)


def ease(local: str, *args, **kwargs):
    """Open a resource that might not exist."""
    path = absolute(local)
    directory, file = os.path.split(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(absolute):
        open(path, "w").close()
    return open(path, *args, **kwargs)
