from collections import deque
from typing import Dict, List, Optional, Set, Tuple


class MazeSolver:
    """
    Finds the shortest path in a bitmask-based maze using BFS.

    Attributes:
        start (Tuple[int, int]): The starting (x, y) coordinates.
        end (Tuple[int, int]): The destination (x, y) coordinates.
        directions (Dict[int, Tuple[int, int, str]]): Mapping of bitmask
            values to movement vectors and direction characters.
    """

    def __init__(self, start: Tuple[int, int], end: Tuple[int, int]) -> None:
        """
        Initialize the solver with start and end points.

        Args:
            start: Starting coordinates.
            end: Target coordinates.
        """
        self.start: Tuple[int, int] = start
        self.end: Tuple[int, int] = end
        self.directions: Dict[int, Tuple[int, int, str]] = {
            1: (0, -1, "N"),
            2: (1, 0, "E"),
            4: (0, 1, "S"),
            8: (-1, 0, "W"),
        }

    def solve(self, grid: List[List[int]]) -> Optional[str]:
        """
        Find the path in the provided grid using Breadth-First Search.

        Args:
            grid: 2D list of bitmask integers representing the maze.

        Returns:
            A string of direction characters (NESW) or None if no path exists.
        """
        if not grid or not grid[0]:
            return None

        height: int = len(grid)
        width: int = len(grid[0])
        queue: deque[Tuple[int, int]] = deque([self.start])
        parent: Dict[
            Tuple[int, int], Tuple[Optional[Tuple[int, int]], str]
        ] = {self.start: (None, "")}
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
        end_node: Tuple[int, int],
    ) -> str:
        """
        Trace back from the end node to the start to build the path string.

        Args:
            parent: Map of nodes to their predecessors and move characters.
            end_node: The destination coordinates.

        Returns:
            The final path string.
        """
        path: List[str] = []
        curr: Optional[Tuple[int, int]] = end_node

        while curr is not None:
            prev_node, direction_char = parent[curr]
            if direction_char:
                path.append(direction_char)
            curr = prev_node

        return "".join(reversed(path))
