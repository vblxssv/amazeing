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
    def generate(self, width: int, height: int, entry: Tuple[int, int],
                 exit: Tuple[int, int], seed: int) -> List[List[int]]:
        random.seed(seed)
        # Изначально всё — сплошные стены (15)
        grid = [[15 for _ in range(width)] for _ in range(height)]
        
        # 1. Параметры паттерна
        pattern_mask = [
            1, 0, 0, 0, 1, 1, 1,
            1, 0, 0, 0, 0, 0, 1,
            1, 1, 1, 0, 1, 1, 1,
            0, 0, 1, 0, 1, 0, 0,
            0, 0, 1, 0, 1, 1, 1,
        ]
        p_w, p_h = 7, 5
        off_x, off_y = (width - p_w) // 2, (height - p_h) // 2
        
        pattern_voids = set()  # Где должны быть проходы (0)
        pattern_walls = set()  # Где должны быть стены (1)
        
        for i, val in enumerate(pattern_mask):
            px, py = i % p_w, i // p_w
            tx, ty = off_x + px, off_y + py
            if 0 <= tx < width and 0 <= ty < height:
                if val == 0:
                    pattern_voids.add((tx, ty))
                else:
                    pattern_walls.add((tx, ty))

        # 2. Пробиваем проходы ВНУТРИ паттерна
        for (x, y) in pattern_voids:
            for dx, dy, bit, opp_bit in [(0, -1, 1, 4), (1, 0, 2, 8), (0, 1, 4, 1), (-1, 0, 8, 2)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in pattern_voids:
                    grid[y][x] &= ~bit
                    grid[ny][nx] &= ~opp_bit

        # 3. Генерация лабиринта (DFS)
        # Важно: паттерн (и стены, и проходы) помечаем как посещенные сразу
        visited = set(pattern_voids) | set(pattern_walls)
        stack = [entry]
        visited.add(entry)
        
        # Чтобы паттерн не был изолирован, соединим его центр с DFS
        # Выбираем любую точку прохода в паттерне (например, среднюю)
        connection_point = (off_x + 3, off_y + 1) 
        
        directions = [(0, -1, 1, 4), (1, 0, 2, 8), (0, 1, 4, 1), (-1, 0, 8, 2)]
        
        while stack:
            cx, cy = stack[-1]
            random.shuffle(directions)
            found = False
            for dx, dy, bit, opp_bit in directions:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < width and 0 <= ny < height:
                    # Если попали на клетку паттерна, которая является проходом (0)
                    if (nx, ny) in pattern_voids and (nx, ny) not in visited:
                         # Эта ветка по сути не нужна, т.к. мы занесли всё в visited сразу
                         pass
                    
                    if (nx, ny) not in visited:
                        grid[cy][cx] &= ~bit
                        grid[ny][nx] &= ~opp_bit
                        visited.add((nx, ny))
                        stack.append((nx, ny))
                        found = True
                        break
            if not found:
                stack.pop()

        # 4. Превращаем в неидеальный (добавляем циклы)
        for y in range(height - 1):
            for x in range(width - 1):
                # Шанс 25% убрать стену
                if random.random() < 0.25:
                    # Условие: не трогаем стены, которые являются частью структуры паттерна
                    self._try_remove_wall(grid, x, y, 2, width, height, pattern_walls)
                if random.random() < 0.25:
                    self._try_remove_wall(grid, x, y, 4, width, height, pattern_walls)

        return grid

    def _try_remove_wall(self, grid, x, y, wall_bit, w, h, forbidden_walls):
        nx, ny = (x + 1, y) if wall_bit == 2 else (x, y + 1)
        
        # Если эта стена — часть обязательного рисунка паттерна, не трогаем
        if (x, y) in forbidden_walls or (nx, ny) in forbidden_walls:
            return

        opp_bit = 8 if wall_bit == 2 else 1
        if nx >= w or ny >= h or not (grid[y][x] & wall_bit):
            return
            
        grid[y][x] &= ~wall_bit
        grid[ny][nx] &= ~opp_bit
        
        # Проверка на 3x3 (чтобы не было пустых площадей)
        if self._is_3x3_area_present(grid, x, y, w, h):
            grid[y][x] |= wall_bit
            grid[ny][nx] |= opp_bit

    def _is_3x3_area_present(self, grid, cx, cy, w, h):
        for start_y in range(max(0, cy - 2), min(h - 2, cy + 1)):
            for start_x in range(max(0, cx - 2), min(w - 2, cx + 1)):
                all_empty = True
                for py in range(start_y, start_y + 3):
                    for px in range(start_x, start_x + 3):
                        # Клетка считается пустой, если у нее убраны внутренние стены квадрата
                        if not self._is_cell_open_to_neighbors(grid, px, py, start_x, start_y):
                            all_empty = False
                            break
                    if not all_empty: break
                if all_empty: return True
        return False

    def _is_cell_open_to_neighbors(self, grid, x, y, x_min, y_min):
        # Проверяем только правую и нижнюю стену внутри текущего окна 3x3
        if x < x_min + 2 and (grid[y][x] & 2): return False
        if y < y_min + 2 and (grid[y][x] & 4): return False
        return True
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
