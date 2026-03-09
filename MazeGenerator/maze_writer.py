from typing import List, Tuple


class MazeWriter:
    """
    Handles the serialization of maze data to text files.

    This class converts the integer grid into a hexadecimal representation
    and appends metadata such as entry/exit points and the solution path.
    """

    def save(
        self,
        grid: List[List[int]],
        entry: Tuple[int, int],
        exit_coords: Tuple[int, int],
        path: str,
        filename: str,
    ) -> None:
        """
        Save the maze grid and metadata to a specified file.

        Args:
            grid: 2D list of integers representing the maze bitmask.
            entry: Starting coordinates of the maze.
            exit_coords: Ending coordinates of the maze.
            path: String of moves representing the solution.
            filename: The target file path for saving.
        """
        try:
            with open(filename, "w", encoding="utf-8") as file:
                for row in grid:
                    hex_row: str = "".join(f"{cell:X}" for cell in row)
                    file.write(hex_row + "\n")

                file.write("\n")
                file.write(f"{entry[0]},{entry[1]}\n")
                file.write(f"{exit_coords[0]},{exit_coords[1]}\n")
                file.write(f"{path}\n")

            print(f"Successfully saved into: {filename}")
        except OSError as error:
            print(f"Error writing: {error}")
