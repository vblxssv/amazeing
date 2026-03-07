from collections import deque
from typing import List, Tuple, Optional, Dict, Set


class MazeSolver:
    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        self.start = start
        self.end = end
        self.directions: Dict[int, Tuple[int, int, str]] = {
            1: (0, -1, 'N'),
            2: (1, 0, 'E'),
            4: (0, 1, 'S'),
            8: (-1, 0, 'W')
        }

    def solve(self, grid: List[List[int]]) -> Optional[str]:
        """Находит путь в переданной сетке grid."""
        if not grid or not grid[0]:
            return None

        height = len(grid)
        width = len(grid[0])
        queue: deque[Tuple[int, int]] = deque([self.start])
        parent: Dict[Tuple[int, int],
                     Tuple[Optional[Tuple[int, int]], str]] = {
            self.start: (None, "")
        }
        visited: Set[Tuple[int, int]] = {self.start}
        while queue:
            cx, cy = queue.popleft()
            if (cx, cy) == self.end:
                return self._reconstruct_path(parent, self.end)
            for bit, (dx, dy, char) in self.directions.items():
                if not (grid[cy][cx] & bit):
                    nx, ny = cx + dx, cy + dy

                    if 0 <= nx < width and 0 <= ny < height:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            parent[(nx, ny)] = ((cx, cy), char)
                            queue.append((nx, ny))
        return None

    def _reconstruct_path(
        self,
        parent: Dict[Tuple[int, int], Tuple[Optional[Tuple[int, int]], str]],
        end_node: Tuple[int, int]
    ) -> str:
        path: List[str] = []
        curr: Optional[Tuple[int, int]] = end_node
        while curr is not None:
            prev_node, direction_char = parent[curr]
            if direction_char:
                path.append(direction_char)
            curr = prev_node
        return "".join(reversed(path))
