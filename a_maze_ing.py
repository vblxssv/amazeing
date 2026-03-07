from typing import List
from MazeGenerator.parser import Parser
import sys
from MazeGenerator.MazeEngine import MazeEngine
from MazeGenerator.path_finder import MazeSolver


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

def print_maze_final(grid, start, path_str="", end=None):
    height = len(grid)
    width = len(grid[0])
    ratio = 2  # Коэффициент горизонтального растяжения

    # Цвета ANSI
    WALL_C = "\033[97m"  # Белый (Стены)
    VOID_C = "\033[90m"  # Серый (Паттерн/Скала)
    PATH_C = "\033[91m"  # Красный (Путь)
    STRT_C = "\033[92m"  # Зеленый (Старт)
    EXIT_C = "\033[96m"  # Голубой (Финиш)
    RESET = "\033[0m"
    
    BLOCK = "█"
    SHADE = "░"
    EMPTY = " "

    # 1. Создаем холст. Размер: (2*W + 1) на (2*H + 1)
    canvas_w = (width * 2 + 1)
    canvas_h = (height * 2 + 1)
    # Инициализируем всё стенами
    canvas = [[f"{WALL_C}{BLOCK}{RESET}" for _ in range(canvas_w * ratio)] 
              for _ in range(canvas_h)]

    def fill_cell(tx, ty, char, color=""):
        """Закрашивает одну логическую координату холста с учетом ratio."""
        fmt = f"{color}{char}{RESET}" if color else char
        for dx in range(ratio):
            canvas[ty][tx * ratio + dx] = fmt

    # 2. Отрисовка структуры (клетки и проходы)
    for y in range(height):
        for x in range(width):
            cell = grid[y][x]
            cx, cy = x * 2 + 1, y * 2 + 1
            
            # Внутренность клетки (проход или паттерн-скала)
            if cell == 15:
                fill_cell(cx, cy, SHADE, VOID_C)
            else:
                fill_cell(cx, cy, EMPTY)

            # Проходы (Битовые маски: 1-N, 2-E, 4-S, 8-W)
            # УБРАНЫ ограничения типа "if cy > 1", чтобы видеть вход/выход на границах
            if not (cell & 1): fill_cell(cx, cy - 1, EMPTY) # North
            if not (cell & 2): fill_cell(cx + 1, cy, EMPTY) # East
            if not (cell & 4): fill_cell(cx, cy + 1, EMPTY) # South
            if not (cell & 8): fill_cell(cx - 1, cy, EMPTY) # West

    # 3. Отрисовка пути (если передан)
    if path_str or start:
        moves = {'N': (0, -1), 'S': (0, 1), 'E': (1, 0), 'W': (-1, 0)}
        curr_x, curr_y = start[0] * 2 + 1, start[1] * 2 + 1
        
        # Начальная точка
        fill_cell(curr_x, curr_y, BLOCK, PATH_C)
        
        for move in path_str:
            dx, dy = moves[move]
            # Закрашиваем стену-проход
            fill_cell(curr_x + dx, curr_y + dy, BLOCK, PATH_C)
            curr_x += dx * 2
            curr_y += dy * 2
            # Закрашиваем следующую клетку
            fill_cell(curr_x, curr_y, BLOCK, PATH_C)

        # 4. Старт и Финиш поверх пути
        fill_cell(start[0] * 2 + 1, start[1] * 2 + 1, BLOCK, STRT_C)
        
        if end:
            ex, ey = end[0] * 2 + 1, end[1] * 2 + 1
        else:
            ex, ey = curr_x, curr_y
        fill_cell(ex, ey, BLOCK, EXIT_C)

    # Вывод
    for row in canvas:
        print("".join(row))

# Пример вызова:
# print_maze_final(grid, (0, 0), "EEEES...", end=(19, 19))

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
        solver = MazeSolver(maze)
        path = solver.solve(mg.entry, mg.exit)
        print(path)
        print_maze_final(maze, mg.entry, path, mg.exit)
        print(F"Entry: {mg.entry}, Exit: {mg.exit}")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{config_path}' не найден.")
    except ValueError as e:
        print(f"Ошибка в конфигурации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
