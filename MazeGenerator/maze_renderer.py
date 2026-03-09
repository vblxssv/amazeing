"""Module for rendering hex-based mazes to the terminal with ANSI colors."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


@dataclass(frozen=True)
class Theme:
    """Represents a visual theme for the maze renderer."""

    name: str
    wall_color: str
    path_color: str


class MazeRenderer:
    """
    Renders a bitmask-based maze into an ASCII/ANSI terminal representation.

    Supports multiple themes, path visualization, and custom scaling.
    """

    RATIO: int = 2
    BLOCK: str = "█"
    SHADE: str = "░"
    EMPTY: str = " "

    THEMES: List[Theme] = [
        Theme("Classic", "\033[97m", "\033[91m"),
        Theme("Hell", "\033[91m", "\033[93m"),
        Theme("Forest", "\033[92m", "\033[95m"),
        Theme("Cyber", "\033[93m", "\033[94m"),
        Theme("Deep Sea", "\033[94m", "\033[96m"),
        Theme("Neon", "\033[95m", "\033[92m"),
    ]

    VOID_C: str = "\033[90m"
    STRT_C: str = "\033[92m"
    EXIT_C: str = "\033[96m"
    RESET: str = "\033[0m"

    def __init__(self) -> None:
        """Initialize the renderer with the default theme."""
        self._current_theme_index: int = 0

    def next_theme(self) -> str:
        """
        Cycle to the next available theme.

        Returns:
            str: The name of the newly activated theme.
        """
        curr_idx = self._current_theme_index
        self._current_theme_index = (curr_idx + 1) % len(self.THEMES)
        return self.THEMES[self._current_theme_index].name

    def get_current_theme_name(self) -> str:
        """
        Retrieve the active theme name.

        Returns:
            str: The current theme name.
        """
        return self.THEMES[self._current_theme_index].name

    def _fill_cell(
        self,
        canvas: List[List[str]],
        tx: int,
        ty: int,
        char: str,
        color: str = ""
    ) -> None:
        """Fill a logical canvas cell based on the RATIO constant."""
        fmt = f"{color}{char}{self.RESET}" if color else char
        for dx in range(self.RATIO):
            canvas[ty][tx * self.RATIO + dx] = fmt

    def render(
        self,
        grid: List[List[int]],
        start: Tuple[int, int],
        path_str: str = "",
        end_coords: Optional[Tuple[int, int]] = None,
        show_path: bool = False
    ) -> None:
        """
        Print the maze to the standard output.

        Args:
            grid: 2D list of bitmask integers.
            start: (x, y) starting coordinates.
            path_str: A string of NESW directions.
            end_coords: (x, y) target coordinates.
            show_path: Whether to draw the path on the maze.
        """
        if not grid or not grid[0]:
            return

        theme = self.THEMES[self._current_theme_index]
        height, width = len(grid), len(grid[0])
        canvas_w, canvas_h = width * 2 + 1, height * 2 + 1

        default_wall = f"{theme.wall_color}{self.BLOCK}{self.RESET}"
        canvas = [
            [default_wall for _ in range(canvas_w * self.RATIO)]
            for _ in range(canvas_h)
        ]

        # Draw grid structure
        for y in range(height):
            for x in range(width):
                cell = grid[y][x]
                cx, cy = x * 2 + 1, y * 2 + 1

                if cell == 15:  # Isolated block
                    self._fill_cell(canvas, cx, cy, self.SHADE, self.VOID_C)
                else:
                    self._fill_cell(canvas, cx, cy, self.EMPTY)

                # Bitwise wall checking: 1=N, 2=E, 4=S, 8=W
                if not (cell & 1):
                    self._fill_cell(canvas, cx, cy - 1, self.EMPTY)
                if not (cell & 2):
                    self._fill_cell(canvas, cx + 1, cy, self.EMPTY)
                if not (cell & 4):
                    self._fill_cell(canvas, cx, cy + 1, self.EMPTY)
                if not (cell & 8):
                    self._fill_cell(canvas, cx - 1, cy, self.EMPTY)

        # Draw path
        curr_x, curr_y = start[0] * 2 + 1, start[1] * 2 + 1
        if show_path and path_str:
            moves: Dict[str, Tuple[int, int]] = {
                'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)
            }
            self._fill_cell(canvas, curr_x, curr_y,
                            self.BLOCK, theme.path_color)
            for move in path_str:
                dx, dy = moves[move]
                # Fill corridor
                self._fill_cell(
                    canvas, curr_x + dx, curr_y + dy, self.BLOCK,
                    theme.path_color
                )
                curr_x += dx * 2
                curr_y += dy * 2
                # Fill destination cell
                self._fill_cell(
                    canvas, curr_x, curr_y, self.BLOCK, theme.path_color
                )

        # Draw Start and Exit markers
        start_cx, start_cy = start[0] * 2 + 1, start[1] * 2 + 1
        self._fill_cell(canvas, start_cx, start_cy, self.BLOCK, self.STRT_C)

        if end_coords:
            ex, ey = end_coords[0] * 2 + 1, end_coords[1] * 2 + 1
        else:
            ex, ey = curr_x, curr_y

        self._fill_cell(canvas, ex, ey, self.BLOCK, self.EXIT_C)

        # Output to terminal
        for row in canvas:
            print("".join(row))
