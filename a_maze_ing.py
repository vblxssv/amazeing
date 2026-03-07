from MazeGenerator.parser import Parser
import sys
from MazeGenerator.maze_engine import MazeEngine


def main() -> None:
    """Entry point of the program. Takes no arguments."""
    if len(sys.argv) != 2:
        print("Using: python3 main.py <path_to_config>")
        print("Example: python main.py maze.conf")
        return
    config_path = sys.argv[1]
    parser = Parser(config_path)

    try:
        args = parser.get_args()
        engine = MazeEngine(*args)
        engine.generate()
        engine.solve()
        engine.show()
        engine.save()
    except FileNotFoundError:
        print(f"Error: File '{config_path}' not found.")
    except ValueError as e:
        print(f"Erorr in config file: {e}")
    except Exception as e:
        print(f"Occured unexpected error: {e}")


if __name__ == "__main__":
    main()
