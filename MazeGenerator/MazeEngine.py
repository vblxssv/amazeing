from abc import ABC, abstractmethod
from typing import List, Tuple
import random


class MazeStrategy(ABC):
    @abstractmethod
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: int) -> List[List[int]]:
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
    # Битовые маски: 1 - стена закрыта, 0 - открыта
    NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

    def __init__(self):
        # Паттерн (1 - закрытая клетка/скала, 0 - обычная клетка)
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
                 exit: Tuple[int, int], seed: int) -> List[List[int]]:
        random.seed(seed)
        
        # Изначально все стены закрыты (15 = 1111)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        
        # Центрирование паттерна
        off_x, off_y = (width - self.p_w) // 2, (height - self.p_h) // 2

        def is_solid(x, y):
            px, py = x - off_x, y - off_y
            if 0 <= px < self.p_w and 0 <= py < self.p_h:
                return self.pattern_mask[py][px] == 1
            return False

        # Сбор доступных стен (только между проходными клетками)
        walls = []
        for y in range(height):
            for x in range(width):
                if is_solid(x, y): continue
                if x < width - 1 and not is_solid(x + 1, y):
                    walls.append(((x, y), (x + 1, y), self.EAST))
                if y < height - 1 and not is_solid(x, y + 1):
                    walls.append(((x, y), (x, y + 1), self.SOUTH))

        random.shuffle(walls)

        # DSU для связности
        parent = {(x, y): (x, y) for x in range(width) for y in range(height)}
        def find(p):
            if parent[p] == p: return p
            parent[p] = find(parent[p])
            return parent[p]

        def union(p1, p2):
            r1, r2 = find(p1), find(p2)
            if r1 != r2:
                parent[r1] = r2
                return True
            return False

        unused_walls = []

        # 1. Генерация связного остова (гарантирует отсутствие тупиковых зон)
        for (c1, c2, d) in walls:
            if union(c1, c2):
                self._open(grid, c1, c2, d)
            else:
                unused_walls.append((c1, c2, d))

        # 2. Добавление циклов с проверкой на пустые области 3x3
        random.shuffle(unused_walls)
        # Пытаемся добавить около 15-20% стен обратно
        for (c1, c2, d) in unused_walls:
            if random.random() < 0.20:
                if not self._creates_3x3_void(grid, c1, c2, d, width, height):
                    self._open(grid, c1, c2, d)

        # 3. Точки входа и выхода
        self._open_ext(grid, entry, width, height)
        self._open_ext(grid, exit, width, height)

        return grid

    def _open(self, grid, c1, c2, d):
        grid[c1[1]][c1[0]] &= ~d
        rev = self.WEST if d == self.EAST else self.NORTH
        grid[c2[1]][c2[0]] &= ~rev

    def _creates_3x3_void(self, grid, c1, c2, d, w, h) -> bool:
        """Проверяет, не образует ли открытие стены 'зал' 3x3."""
        # Временно открываем стену
        self._open(grid, c1, c2, d)
        
        # Проверяем все возможные квадраты 3x3, в которые входят c1 или c2
        found_void = False
        for y in range(max(0, min(c1[1], c2[1]) - 2), min(h - 2, max(c1[1], c2[1]) + 1)):
            for x in range(max(0, min(c1[0], c2[0]) - 2), min(w - 2, max(c1[0], c2[0]) + 1)):
                if self._is_3x3_empty(grid, x, y):
                    found_void = True
                    break
            if found_void: break
        
        # Закрываем обратно, если нашли пустоту
        if found_void:
            grid[c1[1]][c1[0]] |= d
            rev = self.WEST if d == self.EAST else self.NORTH
            grid[c2[1]][c2[0]] |= rev
            
        return found_void

    def _is_3x3_empty(self, grid, sx, sy) -> bool:
        """Проверяет, свободны ли все внутренние перегородки в блоке 3x3."""
        # Вертикальные внутренние перегородки
        for y in range(sy, sy + 3):
            if (grid[y][sx] & self.EAST) or (grid[y][sx+1] & self.EAST):
                return False
        # Горизонтальные внутренние перегородки
        for x in range(sx, sx + 3):
            if (grid[sy][x] & self.SOUTH) or (grid[sy+1][x] & self.SOUTH):
                return False
        return True

    def _open_ext(self, grid, pos, w, h):
        x, y = pos
        if x == 0: grid[y][x] &= ~self.WEST
        elif x == w - 1: grid[y][x] &= ~self.EAST
        if y == 0: grid[y][x] &= ~self.NORTH
        elif y == h - 1: grid[y][x] &= ~self.SOUTH



class MazeEngine:
    def __init__(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], output_file: str, perfect: bool,
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
