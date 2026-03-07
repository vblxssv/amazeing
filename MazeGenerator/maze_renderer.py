
from typing import List, Tuple, Optional, Dict


class MazeRenderer:
    RATIO: int = 2
    BLOCK: str = "█"
    SHADE: str = "░"
    EMPTY: str = " "

    WALL_C: str = "\033[97m"
    VOID_C: str = "\033[90m"
    PATH_C: str = "\033[91m"
    STRT_C: str = "\033[92m"
    EXIT_C: str = "\033[96m"
    RESET: str = "\033[0m"

    def print_maze_final(
        self,
        grid: List[List[int]],
        start: Tuple[int, int],
        path_str: str = "",
        end_coords: Optional[Tuple[int, int]] = None
    ) -> None:
        """Отрисовывает лабиринт в консоли с учетом пути, входа и выхода."""
        if not grid or not grid[0]:
            return

        height = len(grid)
        width = len(grid[0])
        canvas_w = width * 2 + 1
        canvas_h = height * 2 + 1

        default_wall = f"{self.WALL_C}{self.BLOCK}{self.RESET}"
        canvas = [
            [default_wall for _ in range(canvas_w * self.RATIO)]
            for _ in range(canvas_h)
        ]

        def fill_cell(tx: int, ty: int, char: str, color: str = "") -> None:
            """Закрашивает одну логическую координату с учетом RATIO."""
            fmt = f"{color}{char}{self.RESET}" if color else char
            for dx in range(self.RATIO):
                canvas[ty][tx * self.RATIO + dx] = fmt

        for y in range(height):
            for x in range(width):
                cell = grid[y][x]
                cx, cy = x * 2 + 1, y * 2 + 1

                if cell == 15:
                    fill_cell(cx, cy, self.SHADE, self.VOID_C)
                else:
                    fill_cell(cx, cy, self.EMPTY)

                if not (cell & 1):
                    fill_cell(cx, cy - 1, self.EMPTY)
                if not (cell & 2):
                    fill_cell(cx + 1, cy, self.EMPTY)
                if not (cell & 4):
                    fill_cell(cx, cy + 1, self.EMPTY)
                if not (cell & 8):
                    fill_cell(cx - 1, cy, self.EMPTY)

        moves: Dict[str, Tuple[int, int]] = {
            'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)
        }
        curr_x, curr_y = start[0] * 2 + 1, start[1] * 2 + 1

        if path_str or start:
            fill_cell(curr_x, curr_y, self.BLOCK, self.PATH_C)
            for move in path_str:
                if move not in moves:
                    continue
                dx, dy = moves[move]
                fill_cell(curr_x + dx, curr_y + dy, self.BLOCK, self.PATH_C)
                curr_x += dx * 2
                curr_y += dy * 2
                fill_cell(curr_x, curr_y, self.BLOCK, self.PATH_C)

        fill_cell(start[0] * 2 + 1, start[1] * 2 + 1, self.BLOCK, self.STRT_C)

        ex, ey = (
            (end_coords[0] * 2 + 1, end_coords[1] * 2 + 1)
            if end_coords else (curr_x, curr_y)
        )
        fill_cell(ex, ey, self.BLOCK, self.EXIT_C)

        for row in canvas:
            print("".join(row))
