from . import puz
from . import controller, model

import os
crossword_directory = os.path.dirname(__file__)
parent_directory = os.path.dirname(crossword_directory)

def main():
    with open(os.path.join(parent_directory, "puzzles", "Nov0705.puz"), "rb") as puzzle_file:
        puzzle = puz.load(puzzle_file.read())
    m = model.PuzzleModel(puzzle)

    c = controller.Controller()
    c.load_puzzle(m)
    c.main()
