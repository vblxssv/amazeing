from abc import ABC, abstractmethod
import random
from typing import Dict, List, Set, Tuple


class MazeStrategy(ABC):
    """
    Base class for maze generation strategies with shared utilities.

    Attributes:
        N (int): North direction bitmask.
        E (int): East direction bitmask.
        S (int): South direction bitmask.
        W (int): West direction bitmask.
        PATTERN (List[List[int]]): Predefined static obstacle pattern.
        P_H (int): Height of the pattern.
        P_W (int): Width of the pattern.
    """

    N: int = 1
    E: int = 2
    S: int = 4
    W: int = 8
    PATTERN: List[List[int]] = [
        [1, 0, 0, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 0, 1, 1, 1],
        [0, 0, 1, 0, 1, 0, 0],
        [0, 0, 1, 0, 1, 1, 1],
    ]
    P_H: int = 5
    P_W: int = 7

    @abstractmethod
    def generate(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        seed: int,
    ) -> List[List[int]]:
        """
        Abstract method to generate a maze grid.

        Args:
            width: Maze width.
            height: Maze height.
            entry: Entry point coordinates.
            exit_coords: Exit point coordinates.
            seed: Random seed.

        Returns:
            The generated grid as a 2D list of integers.
        """
        pass

    def _open(
        self,
        grid: List[List[int]],
        c1: Tuple[int, int],
        c2: Tuple[int, int],
        d: int,
    ) -> None:
        """
        Remove the wall between two adjacent cells.

        Args:
            grid: The maze grid.
            c1: First cell coordinates.
            c2: Second cell coordinates.
            d: Direction from c1 to c2.
        """
        grid[c1[1]][c1[0]] &= ~d
        rev: int = self.E
        if d == self.N:
            rev = self.S
        elif d == self.S:
            rev = self.N
        elif d == self.E:
            rev = self.W

        grid[c2[1]][c2[0]] &= ~rev

    def _open_ext(
        self, grid: List[List[int]], pos: Tuple[int, int], w: int, h: int
    ) -> None:
        """
        Open a wall on the outer boundary of the maze.

        Args:
            grid: The maze grid.
            pos: Position on the boundary.
            w: Maze width.
            h: Maze height.
        """
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
    """Kruskal's algorithm implementation for generating a perfect maze."""

    def generate(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        seed: int,
    ) -> List[List[int]]:
        """Generate a perfect maze using Kruskal's algorithm."""
        random.seed(seed)
        grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]
        can_fit = width >= 9 and height >= 7
        blocked: Set[Tuple[int, int]] = set()

        if can_fit:
            ox: int = (width - self.P_W) // 2
            oy: int = (height - self.P_H) // 2
            for py in range(self.P_H):
                for px in range(self.P_W):
                    if self.PATTERN[py][px] == 1:
                        blocked.add((ox + px, oy + py))

        parent: Dict[Tuple[int, int], Tuple[int, int]] = {
            (x, y): (x, y) for y in range(height) for x in range(width)
        }

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
                self._open(grid, (x1, y1), (x2, y2), direction)
        return grid


class NonPerfectMazeGen(MazeStrategy):
    """Generates a non-perfect maze using Kruskal's with cycle injection."""

    def generate(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        seed: int,
    ) -> List[List[int]]:
        """Generate a non-perfect maze with potential cycles."""
        random.seed(seed)
        grid: List[List[int]] = [
            [15 for _ in range(width)] for _ in range(height)
        ]

        can_fit = width >= 9 and height >= 7
        off_x = (width - self.P_W) // 2 if can_fit else 0
        off_y = (height - self.P_H) // 2 if can_fit else 0

        def is_solid(x: int, y: int) -> bool:
            if not can_fit:
                return False
            px, py = x - off_x, y - off_y
            if 0 <= px < self.P_W and 0 <= py < self.P_H:
                return self.PATTERN[py][px] == 1
            return False

        walls: List[Tuple[Tuple[int, int], Tuple[int, int], int]] = []
        for y in range(height):
            for x in range(width):
                if is_solid(x, y):
                    continue
                if x < width - 1 and not is_solid(x + 1, y):
                    walls.append(((x, y), (x + 1, y), self.E))
                if y < height - 1 and not is_solid(x, y + 1):
                    walls.append(((x, y), (x, y + 1), self.S))

        random.shuffle(walls)
        parent: Dict[Tuple[int, int], Tuple[int, int]] = {
            (x, y): (x, y) for x in range(width) for y in range(height)
        }

        def find(p: Tuple[int, int]) -> Tuple[int, int]:
            if parent[p] == p:
                return p
            parent[p] = find(parent[p])
            return parent[p]

        unused_walls = []
        for c1, c2, d in walls:
            r1, r2 = find(c1), find(c2)
            if r1 != r2:
                parent[r1] = r2
                self._open(grid, c1, c2, d)
            else:
                unused_walls.append((c1, c2, d))

        random.shuffle(unused_walls)
        for c1, c2, d in unused_walls:
            if random.random() < 0.20:
                if not self._creates_3x3_void(grid, c1, c2, d, width, height):
                    self._open(grid, c1, c2, d)
        return grid

    def _creates_3x3_void(
        self,
        grid: List[List[int]],
        c1: Tuple[int, int],
        c2: Tuple[int, int],
        d: int,
        w: int,
        h: int,
    ) -> bool:
        """Check if opening a wall creates a 3x3 empty square."""
        self._open(grid, c1, c2, d)
        found_void: bool = False
        y_range = range(
            max(0, min(c1[1], c2[1]) - 2),
            min(h - 2, max(c1[1], c2[1]) + 1)
        )
        x_range = range(
            max(0, min(c1[0], c2[0]) - 2),
            min(w - 2, max(c1[0], c2[0]) + 1)
        )
        for y in y_range:
            for x in x_range:
                if self._is_3x3_empty(grid, x, y):
                    found_void = True
                    break
            if found_void:
                break

        if found_void:
            grid[c1[1]][c1[0]] |= d
            if d == self.E:
                grid[c2[1]][c2[0]] |= self.W
            elif d == self.S:
                grid[c2[1]][c2[0]] |= self.N
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
