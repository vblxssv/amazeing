import sys
from typing import Tuple

from MazeGenerator.maze_engine import MazeEngine
from MazeGenerator.parser import Parser


def print_menu() -> None:
    """Print the user command menu."""
    print("\n--- Maze Generator Menu ---")
    print("g - Generate new maze (autosave to file)")
    print("s - Show/Hide solution path")
    print("t - Next theme")
    print("q - Quit")
    print("---------------------------")


def main() -> None:
    """Run the main interactive CLI loop."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <path_to_config>")
        return

    config_path: str = sys.argv[1]
    parser: Parser = Parser(config_path)

    try:
        args: Tuple[
            int, int, Tuple[int, int], Tuple[int, int], str, bool, int
        ] = parser.get_args()
        engine: MazeEngine = MazeEngine(*args)
        engine.generate()
        engine.solve()
        engine.save()

        show_path: bool = True
        while True:
            print("\033[H\033[J", end="")
            theme_name: str = engine.renderer.get_current_theme_name()
            print(f"Current Theme: {theme_name}")
            print(f"Output File: {engine.output_file} (Autosaved)")

            engine.show(with_path=show_path)
            print_menu()

            choice: str = input("Select action: ").lower().strip()

            if choice == "g":
                engine.seed += 1
                engine.generate()
                engine.solve()
                engine.save()
            elif choice == "s":
                show_path = not show_path
            elif choice == "t":
                engine.renderer.next_theme()
            elif choice == "q":
                print("Goodbye!")
                break
            else:
                input("Invalid command. Press Enter to try again...")

    except FileNotFoundError:
        print(f"Error: File '{config_path}' not found.")
    except ValueError as error:
        print(f"Error in config file: {error}")
    except OSError as error:
        print(f"System error: {error}")


if __name__ == "__main__":
    main()
