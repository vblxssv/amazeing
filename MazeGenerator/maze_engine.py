from typing import Tuple, List
from MazeGenerator.path_finder import MazeSolver
from MazeGenerator.maze_writer import MazeWriter
from MazeGenerator.maze_renderer import MazeRenderer
from MazeGenerator.maze_generator import MazeStrategy, PerfectMazeGen
from MazeGenerator.maze_generator import NonPerfectMazeGen


class MazeEngine:
    def __init__(
        self,
        width: int,
        height: int,
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        output_file: str,
        perfect: bool,
        seed: int
    ) -> None:
        """Initialize the maze engine with all necessary components."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit_coords
        self.output_file = output_file
        self.seed = seed

        self.algorithm: MazeStrategy = (
            PerfectMazeGen() if perfect else NonPerfectMazeGen()
        )

        self.writer = MazeWriter()
        self.solver = MazeSolver(self.entry, self.exit)
        self.renderer = MazeRenderer()

        self.maze: List[List[int]] = []
        self.path: str = ""

    def generate(self) -> None:
        """Generate a new maze using the selected strategy."""
        self.maze = self.algorithm.generate(
            self.width, self.height, self.entry, self.exit, self.seed
        )
        self.path = ""

    def solve(self) -> None:
        """Solve the generated maze and store the path."""
        if not self.maze:
            self.generate()

        solution = self.solver.solve(self.maze)
        self.path = solution if solution else ""

    def save(self) -> None:
        """Save the maze and solution metadata to a hex file."""
        if not self.maze:
            self.generate()
        self.writer.save(
            self.maze, self.entry, self.exit, self.path, self.output_file
        )

    def show(self) -> None:
        """Render the maze and solution path to the console."""
        if not self.maze:
            self.generate()
        self.renderer.print_maze_final(
            self.maze, self.entry, self.path, self.exit
        )
