import random
from abc import ABC, abstractmethod
from typing import List, Tuple


class MazeStrategy(ABC):
    """Base class for maze generation strategies with shared utilities."""
    N, E, S, W = 1, 2, 4, 8
    PATTERN = [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    P_H, P_W = 5, 7

    @abstractmethod
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
        """Abstract method to generate a maze grid."""
        pass

    def _open(self, grid: List[List[int]], c1: Tuple[int, int],
              c2: Tuple[int, int], d: int) -> None:
        """Remove the wall between two adjacent cells."""
        grid[c1[1]][c1[0]] &= ~d
        rev = self.W if d == self.E else self.N
        grid[c2[1]][c2[0]] &= ~rev

    def _open_ext(self, grid: List[List[int]], pos: Tuple[int, int],
                  w: int, h: int) -> None:
        """Open a wall on the outer boundary of the maze."""
        x, y = pos
        if x == 0:
            grid[y][x] &= ~self.W
        elif x == w - 1:
            grid[y][x] &= ~self.E
        if y == 0:
            grid[y][x] &= ~self.N
        elif y == h - 1:
            grid[y][x] &= ~self.S


class PerfectMazeGen(MazeStrategy):
    """
    Kruskal's algorithm implementation for generating a perfect maze
    while respecting a central wall pattern.
    """
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
        random.seed(seed)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        ox, oy = (width - self.P_W) // 2, (height - self.P_H) // 2

        parent = {(x, y): (x, y) for y in range(height) for x in range(width)}

        def find(i: Tuple[int, int]) -> Tuple[int, int]:
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i: Tuple[int, int], j: Tuple[int, int]) -> bool:
            root_i, root_j = find(i), find(j)
            if root_i != root_j:
                parent[root_i] = root_j
                return True
            return False

        blocked: set[Tuple[int, int]] = set()
        for py in range(self.P_H):
            for px in range(self.P_W):
                if self.PATTERN[py][px] == 1:
                    blocked.add((ox + px, oy + py))

        edges: List[Tuple[Tuple[int, int], Tuple[int, int], int]] = []
        for y in range(height):
            for x in range(width):
                if (x, y) in blocked:
                    continue
                if x < width - 1 and (x + 1, y) not in blocked:
                    edges.append(((x, y), (x + 1, y), self.E))
                if y < height - 1 and (x, y + 1) not in blocked:
                    edges.append(((x, y), (x, y + 1), self.S))

        random.shuffle(edges)

        for (x1, y1), (x2, y2), direction in edges:
            if union((x1, y1), (x2, y2)):
                if direction == self.E:
                    self._open(grid, (x1, y1), (x2, y2), self.E)
                elif direction == self.S:
                    grid[y1][x1] &= ~self.S
                    grid[y2][x2] &= ~self.N
        return grid


class NonPerfectMazeGen(MazeStrategy):
    """Generates a non-perfect maze using Kruskal's with cycle injection."""

    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit_coords: Tuple[int, int], seed: int) -> List[List[int]]:
        """Generate a maze with possible loops and multiple paths."""
        random.seed(seed)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        off_x, off_y = (width - self.P_W) // 2, (height - self.P_H) // 2

        def is_solid(x: int, y: int) -> bool:
            px, py = x - off_x, y - off_y
            if 0 <= px < self.P_W and 0 <= py < self.P_H:
                return self.PATTERN[py][px] == 1
            return False

        walls = []
        for y in range(height):
            for x in range(width):
                if is_solid(x, y):
                    continue
                if x < width - 1 and not is_solid(x + 1, y):
                    walls.append(((x, y), (x + 1, y), self.E))
                if y < height - 1 and not is_solid(x, y + 1):
                    walls.append(((x, y), (x, y + 1), self.S))

        random.shuffle(walls)
        parent = {(x, y): (x, y) for x in range(width) for y in range(height)}

        def find(p):
            if parent[p] == p:
                return p
            parent[p] = find(parent[p])
            return parent[p]

        unused_walls = []
        for (c1, c2, d) in walls:
            root1, root2 = find(c1), find(c2)
            if root1 != root2:
                parent[root1] = root2
                self._open(grid, c1, c2, d)
            else:
                unused_walls.append((c1, c2, d))

        random.shuffle(unused_walls)
        for (c1, c2, d) in unused_walls:
            if random.random() < 0.20:
                if not self._creates_3x3_void(grid, c1, c2, d, width, height):
                    self._open(grid, c1, c2, d)
        return grid

    def _creates_3x3_void(self, grid: List[List[int]], c1: Tuple[int, int],
                          c2: Tuple[int, int], d: int, w: int, h: int) -> bool:
        """Check if opening a wall creates a 3x3 empty square."""
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
            rev = self.W if d == self.E else self.N
            grid[c2[1]][c2[0]] |= rev
        return found_void

    def _is_3x3_empty(self, grid: List[List[int]], sx: int, sy: int) -> bool:
        """Determine if a 3x3 block of cells has no internal walls."""
        for y in range(sy, sy + 3):
            if (grid[y][sx] & self.E) or (grid[y][sx + 1] & self.E):
                return False
        for x in range(sx, sx + 3):
            if (grid[sy][x] & self.S) or (grid[sy + 1][x] & self.S):
                return False
        return True
