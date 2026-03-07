from typing import List, Tuple


class MazeWriter:
    def save(self, grid: List[List[int]], entry: Tuple[int, int],
             exit: Tuple[int, int], path: str, filename: str):
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for row in grid:
                    hex_row = "".join(f"{cell:X}" for cell in row)
                    f.write(hex_row + "\n")
                f.write("\n")
                f.write(f"{entry[0]},{entry[1]}\n")
                f.write(f"{exit[0]},{exit[1]}\n")
                f.write(f"{path}\n")
            print(f"Successfully saved into: {filename}")
        except Exception as e:
            print(f"Error writing: {e}")
