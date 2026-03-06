from abc import ABC, abstractmethod
from typing import List, Tuple
import random


class MazeStrategy(ABC):
    @abstractmethod
    def generate(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], seed: int) -> List[List[int]]:
        pass


class PerfectMazeGen(MazeStrategy):
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: int) -> List[List[int]]:
        random.seed(seed)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        pattern_mask = [
            1, 0, 0, 0, 1, 1, 1,
            1, 0, 0, 0, 0, 0, 1,
            1, 1, 1, 0, 1, 1, 1,
            0, 0, 1, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 1,
        ]
        p_w, p_h = 7, 5
        offset_x = (width - p_w) // 2
        offset_y = (height - p_h) // 2
        visited = set()
        for i, val in enumerate(pattern_mask):
            px, py = i % p_w, i // p_w
            target_x, target_y = offset_x + px, offset_y + py
            if val == 1:
                visited.add((target_x, target_y))
        stack = [entry]
        visited.add(entry)
        directions = [
            (0, -1, 1, 4),
            (1, 0, 2, 8),
            (0, 1, 4, 1),
            (-1, 0, 8, 2)
        ]
        while stack:
            cx, cy = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy, bit, opp_bit in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited: # noqa
                    grid[cy][cx] &= ~bit
                    grid[ny][nx] &= ~opp_bit
                    visited.add((nx, ny))
                    stack.append((nx, ny))
                    found = True
                    break
            if not found:
                stack.pop()
        ex, ey = entry
        grid[ey][ex] &= ~8
        return grid


class NonPerfectMazeGen(MazeStrategy):
    def generate(self, width, height, entry, exit, seed) -> List[List[int]]:
        pass


class MazeEngine:
    def __init__(self, width: int, height: int, entry: tuple[int, int],
                 exit: tuple[int, int], output_file: str, perfect: bool,
                 seed: int):
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.output_file = output_file
        self.seed = seed
        if perfect:
            self.algorithm = PerfectMazeGen()
        else:
            self.algorithm = NonPerfectMazeGen()

    def generate(self) -> List[List[int]]:
        return self.algorithm.generate(self.width, self.height,
                                       self.entry, self.exit, self.seed)
