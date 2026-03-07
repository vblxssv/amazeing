from collections import deque
from typing import List, Tuple, Optional


class MazeSolver:
    def __init__(self, grid: List[List[int]]):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0])
        # Соответствие битов направлениям
        self.directions = {
            1: (0, -1, 'N'),  # North
            2: (1, 0, 'E'),   # East
            4: (0, 1, 'S'),   # South
            8: (-1, 0, 'W')   # West
        }

    def solve(self, start: Tuple[int, int],
              end: Tuple[int, int]) -> Optional[str]:
        """Находит путь от start до end и возвращает его как строку."""
        queue = deque([start])
        # parent хранит (откуда пришли, символ направления)
        parent = {start: (None, "")}
        visited = {start}

        while queue:
            cx, cy = queue.popleft()

            if (cx, cy) == end:
                return self._reconstruct_path(parent, end)

            # Проверяем все 4 направления через битовую маску
            for bit, (dx, dy, char) in self.directions.items():
                # Если бит НЕ установлен, значит стены НЕТ (проход открыт)
                if not (self.grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy

                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = ((cx, cy), char)
                            queue.append((nx, ny))
        return None

    def _reconstruct_path(self, parent, end_node) -> str:
        path = []
        curr = end_node
        while parent[curr][0] is not None:
            prev_node, direction_char = parent[curr]
            path.append(direction_char)
            curr = prev_node
        return "".join(reversed(path))
