from typing import List
from parser import Parser
import sys
from MazeGenerator.MazeEngine import MazeEngine
import mlx


def save_maze_as_hex(grid: List[List[int]], filename: str):
    """
    Сохраняет лабиринт в файл, где каждое число 0-15
    представлено как один Hex-символ (0-F).
    """
    try:
        with open(filename, 'w') as f:
            for row in grid:
                hex_row = "".join(f"{cell:X}" for cell in row)
                f.write(hex_row + "\n")
        print(f"Лабиринт успешно сохранен в файл: {filename}")
    except Exception as e:
        print(f"Ошибка при записи в файл: {e}")



class MazeApp:
    def __init__(self, maze, tile_size=32):
        self.maze = maze
        self.tile_size = tile_size
        self.width = len(maze[0]) * tile_size
        self.height = len(maze) * tile_size
        
        # Инициализация MLX
        self.m = mlx.init()
        self.win = self.m.new_window(self.width, self.height, "A-maze-ing")
        
    def draw_maze(self):
        for y, row in enumerate(self.maze):
            for x, cell in enumerate(row):
                # Рисуем пол/стены в зависимости от битов (cell)
                # Например, если cell == 15 (F), рисуем квадрат стены
                color = 0xFFFFFF if cell == 15 else 0x000000
                self.draw_tile(x, y, color)

    def draw_tile(self, x, y, color):
        # Простой пример закраски квадрата пиксель за пикселем
        start_x = x * self.tile_size
        start_y = y * self.tile_size
        for i in range(self.tile_size):
            for j in range(self.tile_size):
                self.m.pixel_put(self.win, start_x + i, start_y + j, color)

    def run(self):
        self.draw_maze()
        self.m.loop()





def main():

    if len(sys.argv) != 2:
        print("Использование: python main.py <путь_к_конфигу>")
        print("Пример: python main.py maze.conf")
        return
    config_path = sys.argv[1]
    parser = Parser(config_path)

    try:
        args = parser.get_args_tuple()
        print(f"Конфигурация '{config_path}' успешно загружена.")
        mg = MazeEngine(*args)
        maze = mg.generate()
        save_maze_as_hex(maze, mg.output_file)
        ma = MazeApp(maze, 20)
        ma.draw_maze()
    except FileNotFoundError:
        print(f"Ошибка: Файл '{config_path}' не найден.")
    except ValueError as e:
        print(f"Ошибка в конфигурации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
