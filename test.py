import puz
def get_full_solution(puzzle):
    """Return the full solution as a list with rebus entries."""
    solution = list(puzzle.solution)
    rebus = puzzle.rebus()
    for index in rebus.get_rebus_squares():
        solution[index] = rebus.solutions[rebus.table[index] - 1]
    return solution
