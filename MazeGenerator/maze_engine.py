from typing import List, Optional, Tuple

from MazeGenerator.maze_generator import (
    MazeStrategy,
    NonPerfectMazeGen,
    PerfectMazeGen,
)
from MazeGenerator.maze_renderer import MazeRenderer
from MazeGenerator.maze_writer import MazeWriter
from MazeGenerator.path_finder import MazeSolver


class MazeEngine:
    """
    Orchestrates maze generation, solving, saving, and rendering.

    Attributes:
        width (int): The width of the maze grid.
        height (int): The height of the maze grid.
        entry (Tuple[int, int]): Starting coordinates.
        exit_coords (Tuple[int, int]): Ending coordinates.
        output_file (str): Path to the destination file.
        seed (int): Random seed for generation.
        algorithm (MazeStrategy): The strategy used for generation.
        writer (MazeWriter): Component for file operations.
        solver (MazeSolver): Component for finding paths.
        renderer (MazeRenderer): Component for visual output.
        maze (List[List[int]]): The generated grid structure.
        path (str): The string representation of the solution path.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: int,
    ) -> None:
        """
        Initialize the maze engine with its required components.

        Args:
            width: Width of the grid.
            height: Height of the grid.
            entry: Start coordinates.
            exit_coords: Target coordinates.
            output_file: Storage path.
            perfect: Whether to use the perfect maze algorithm.
            seed: Randomization seed.
        """
        self.width: int = width
        self.height: int = height
        self.entry: Tuple[int, int] = entry
        self.exit_coords: Tuple[int, int] = exit_coords
        self.output_file: str = output_file
        self.seed: int = seed

        self.algorithm: MazeStrategy = (
            PerfectMazeGen() if perfect else NonPerfectMazeGen()
        )

        self.writer: MazeWriter = MazeWriter()
        self.solver: MazeSolver = MazeSolver(self.entry, self.exit_coords)
        self.renderer: MazeRenderer = MazeRenderer()

        self.maze: List[List[int]] = []
        self.path: str = ""

    def generate(self) -> None:
        """Generate a new maze using the selected strategy."""
        self.maze = self.algorithm.generate(
            self.width, self.height, self.entry, self.exit_coords, self.seed
        )
        self.path = ""

    def solve(self) -> None:
        """Solve the generated maze and store the solution path."""
        if not self.maze:
            self.generate()

        solution: Optional[str] = self.solver.solve(self.maze)
        self.path = solution if solution is not None else ""

    def save(self) -> None:
        """Save the maze and solution metadata to the output file."""
        if not self.maze:
            self.generate()
        self.writer.save(
            self.maze, self.entry, self.exit_coords,
            self.path, self.output_file
        )

    def show(self, with_path: bool = False) -> None:
        """
        Render the maze to the console.

        Args:
            with_path: If True, renders the solved path on the maze.
        """
        if not self.maze:
            self.generate()
        self.renderer.render(
            grid=self.maze,
            start=self.entry,
            path_str=self.path,
            end_coords=self.exit_coords,
            show_path=with_path,
        )
