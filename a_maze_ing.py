from parser import Parser
import sys


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
        print(f"Параметры: {args}")
    except FileNotFoundError:
        print(f"Ошибка: Файл '{config_path}' не найден.")
    except ValueError as e:
        print(f"Ошибка в конфигурации: {e}")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    main()
