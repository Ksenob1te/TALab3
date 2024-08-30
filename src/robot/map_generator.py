from typing import List, Tuple
import random

def generate_map(size: int = 5) -> List[List[int]]:
    def checkNeighbors(_y_pos, _x_pos):
        neighbors = []

        top = None
        right = None
        bottom = None
        left = None

        if (_y_pos > 1):
            top = grid[_y_pos - 2][_x_pos]

        if (_x_pos < size - 2):
            right = grid[_y_pos][_x_pos + 2]

        if (_y_pos < size - 2):
            bottom = grid[_y_pos + 2][_x_pos]

        if (_x_pos > 1):
            left = grid[_y_pos][_x_pos - 2]

        if top:
            neighbors.append((_y_pos - 2, _x_pos))
        if right and not right.visited:
            neighbors.append((_y_pos, _x_pos + 2))
        if bottom and not bottom.visited:
            neighbors.append((_y_pos + 2, _x_pos))
        if left and not left.visited:
            neighbors.append((_y_pos, _x_pos - 2))

        if len(neighbors) > 0:
            r = random.randint(0, len(neighbors) - 1)
            return neighbors[r]
        else:
            return None

    grid = []
    for y in range(size):
        grid.append([])
        for x in range(size):
            grid[y].append("1")

    visited: List[Tuple[int, int]] = []
    x_pos = 1
    y_pos = 1
    current_cell = grid[1][1]
    stack = []
    done = False

    while not done:
        current_cell.visited = True
        next_cell = current_cell.checkNeighbors()
        if next_cell != None:
            stack.append(current_cell)
            current_cell[x_pos][y_pos] = "0"
            removeWalls(current_cell, next_cell)
            current_cell = next_cell
        elif len(stack) > 0:
            current_cell = stack.pop()
        else:
            done = True
