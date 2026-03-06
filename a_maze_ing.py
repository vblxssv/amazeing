from typing import List
from MazeGenerator.parser import Parser
import sys
from MazeGenerator.MazeEngine import MazeEngine


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

def print_maze(grid):
    height = len(grid)
    width = len(grid[0])
    
    # Верхняя граница всего лабиринта
    output = " " + "_" * (width * 2 - 1) + "\n"
    
    for y in range(height):
        output += "|" # Левая граница
        for x in range(width):
            cell = grid[y][x]
            
            # Проверяем нижнюю стену (бит 4)
            # Если бит установлен — рисуем подчеркивание (стену)
            bottom = "_" if (cell & 4) else " "
            
            # Проверяем правую стену (бит 2)
            # Если бит установлен — рисуем вертикальную черту
            right = "|" if (cell & 2) else " "
            
            # Если мы на последней клетке строки, правая стена всегда должна быть,
            # но мы берем её из маски клетки
            output += bottom + right
            
        output += "\n"
    print(output)




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
        print_maze(maze)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{config_path}' не найден.")
    except ValueError as e:
        print(f"Ошибка в конфигурации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
