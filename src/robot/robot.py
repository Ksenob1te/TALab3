from typing import List, Tuple, Union, Dict
import os
import time
class Robot:
    position: List[int] = [0, 0]
    imported_map: List[List[int]] = None
    path_log: List[Tuple[int, int]] = None
    memory: Dict[str, Tuple[int, int]] = None

    def __init__(self):
        self.path_log = []
        self.memory = {}
        self.position = [1, 1]
        self.imported_map = []

    def import_config(self, file_path: str):
        with open(file_path, "r") as f:
            self.position = list(map(int, f.readline().split()))
            self.imported_map = [[int(i) for i in line.split()] for line in f.readlines()]

    def draw_map(self):
        for i in range(len(self.imported_map)):
            for j in range(len(self.imported_map[i])):
                if self.position[0] == i and self.position[1] == j:
                    print("R", end=" ")
                elif self.imported_map[i][j] == 0:
                    print("_", end=" ")
                else:
                    print("#", end=" ")
            print()

    def set_pos(self, new_pos: Tuple[int, int]):
        x = new_pos[0]
        y = new_pos[1]
        self.position[0] = x
        self.position[1] = y
        self.path_log.append(new_pos)
        print(f"Robot has moved to position ({x}, {y}).")
        if self.imported_map[x][y] == 0:
            os.system('clear')
            self.draw_map()
            time.sleep(0.2)
            if x == 0 or x == len(self.imported_map) - 1 or y == 0 or y == len(self.imported_map[0]) - 1:
                print(f"Robot has reached the exit at position ({x}, {y}).\nPath: {self.path_log}")
                exit(0)

    def timeshift(self, value: Union[int, str]):
        if type(value) is str:
            if value not in self.memory:
                raise RuntimeError(f"Key '{value}' does not exist in memory.")
            value = self.memory[value]
            self.set_pos(value)

        elif type(value) is int:
            if value < 0:
                raise ValueError(f"Value must be greater than 0, not {value}.")
            if value > len(self.path_log):
                value = len(self.path_log)
            prev_pos = self.path_log[-value]
            self.set_pos(prev_pos)

    def bind(self, key: str):
        self.memory[key] = (self.position[0], self.position[1])

    def move_top(self):
        if self.position[0] > 0 and self.imported_map[self.position[0] - 1][self.position[1]] == 0:
            self.set_pos((self.position[0] - 1, self.position[1]))
            return 1
        return 0

    def move_down(self):
        if self.position[0] < len(self.imported_map) - 1 and self.imported_map[self.position[0] + 1][self.position[1]] == 0:
            self.set_pos((self.position[0] + 1, self.position[1]))
            return 1
        return 0

    def move_left(self):
        if self.position[1] > 0 and self.imported_map[self.position[0]][self.position[1] - 1] == 0:
            self.set_pos((self.position[0], self.position[1] - 1))
            return 1
        return 0

    def move_right(self):
        if self.position[1] < len(self.imported_map[0]) - 1 and self.imported_map[self.position[0]][self.position[1] + 1] == 0:
            self.set_pos((self.position[0], self.position[1] + 1))
            return 1
        return 0


global_robot: Robot = Robot()
global_robot.import_config("./src/robot/configs/3.config")