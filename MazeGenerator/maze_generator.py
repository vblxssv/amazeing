from abc import ABC, abstractmethod
from typing import List, Tuple, Set, Dict
import random


class MazeStrategy(ABC):
    @abstractmethod
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
        pass


class PerfectMazeGen(MazeStrategy):
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
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
        visited: Set[Tuple[int, int]] = set()
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
                if 0 <= nx < width and 0 <= ny < height and \
                   (nx, ny) not in visited:
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
    NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

    def __init__(self) -> None:
        self.pattern_mask = [
            [1, 0, 0, 0, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1],
        ]
        self.p_h = len(self.pattern_mask)
        self.p_w = len(self.pattern_mask[0])

    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
        random.seed(seed)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        off_x, off_y = (width - self.p_w) // 2, (height - self.p_h) // 2

        def is_solid(x: int, y: int) -> bool:
            px, py = x - off_x, y - off_y
            if 0 <= px < self.p_w and 0 <= py < self.p_h:
                return self.pattern_mask[py][px] == 1
            return False

        walls = []
        for y in range(height):
            for x in range(width):
                if is_solid(x, y):
                    continue
                if x < width - 1 and not is_solid(x + 1, y):
                    walls.append(((x, y), (x + 1, y), self.EAST))
                if y < height - 1 and not is_solid(x, y + 1):
                    walls.append(((x, y), (x, y + 1), self.SOUTH))

        random.shuffle(walls)
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {
            (x, y): (x, y) for x in range(width) for y in range(height)
        }

        def find(p: Tuple[int, int]) -> Tuple[int, int]:
            if parent[p] == p:
                return p
            parent[p] = find(parent[p])
            return parent[p]

        def union(p1: Tuple[int, int], p2: Tuple[int, int]) -> bool:
            r1, r2 = find(p1), find(p2)
            if r1 != r2:
                parent[r1] = r2
                return True
            return False

        unused_walls = []
        for (c1, c2, d) in walls:
            if union(c1, c2):
                self._open(grid, c1, c2, d)
            else:
                unused_walls.append((c1, c2, d))

        random.shuffle(unused_walls)
        for (c1, c2, d) in unused_walls:
            if random.random() < 0.20:
                if not self._creates_3x3_void(grid, c1, c2, d, width, height):
                    self._open(grid, c1, c2, d)

        self._open_ext(grid, entry, width, height)
        self._open_ext(grid, exit_coords, width, height)
        return grid

    def _open(self, grid: List[List[int]], c1: Tuple[int, int],
              c2: Tuple[int, int], d: int) -> None:
        grid[c1[1]][c1[0]] &= ~d
        rev = self.WEST if d == self.EAST else self.NORTH
        grid[c2[1]][c2[0]] &= ~rev

    def _creates_3x3_void(self, grid: List[List[int]], c1: Tuple[int, int],
                          c2: Tuple[int, int], d: int, w: int, h: int) -> bool:
        self._open(grid, c1, c2, d)
        found_void = False
        y_range = range(max(0, min(c1[1], c2[1]) - 2),
                        min(h - 2, max(c1[1], c2[1]) + 1))
        x_range = range(max(0, min(c1[0], c2[0]) - 2),
                        min(w - 2, max(c1[0], c2[0]) + 1))
        for y in y_range:
            for x in x_range:
                if self._is_3x3_empty(grid, x, y):
                    found_void = True
                    break
            if found_void:
                break
        if found_void:
            grid[c1[1]][c1[0]] |= d
            rev = self.WEST if d == self.EAST else self.NORTH
            grid[c2[1]][c2[0]] |= rev
        return found_void

    def _is_3x3_empty(self, grid: List[List[int]], sx: int, sy: int) -> bool:
        for y in range(sy, sy + 3):
            if (grid[y][sx] & self.EAST) or (grid[y][sx + 1] & self.EAST):
                return False
        for x in range(sx, sx + 3):
            if (grid[sy][x] & self.SOUTH) or (grid[sy + 1][x] & self.SOUTH):
                return False
        return True

    def _open_ext(self, grid: List[List[int]], pos: Tuple[int, int],
                  w: int, h: int) -> None:
        x, y = pos
        if x == 0:
            grid[y][x] &= ~self.WEST
        elif x == w - 1:
            grid[y][x] &= ~self.EAST
        if y == 0:
            grid[y][x] &= ~self.NORTH
        elif y == h - 1:
            grid[y][x] &= ~self.SOUTH
