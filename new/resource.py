"""A collection of various file system tools."""

# Import
import os
import io


# Main functions
def absolute(local: str) -> str:
    """Get the absolute path of a local file or directory."""
    return os.path.abspath(local)


def check(local: str) -> bool:
    """Check if a local path exists."""
    path = absolute(local)
    return os.path.exists(path)


def need(local: str, mode: str="r"):
    """Open a resource that has to exist."""
    path = absolute(local)
    return open(path, mode)


def ease(local: str, mode: str="r", copy: str="\n") -> io.TextIOWrapper:
    """Open a resource that might not exist."""
    path = absolute(local)
    directory, file = os.path.split(path)
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(path):
        with open(path, "w") as file:
            file.write(copy)
            file.close()
    return open(file, mode)


def read(local: str):
    """Read a reource."""
    with need(local) as file:
        return file.read()
